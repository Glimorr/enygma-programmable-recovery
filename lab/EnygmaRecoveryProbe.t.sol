// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

// OFFLINE CONTRACT LAB ONLY. Deliberately invokes an authorized relayer twice.
// It does NOT establish that a real Enygma relayer/CTS retry can do so.
import {Test} from "forge-std/Test.sol";
import {ERC1967Proxy} from "@openzeppelin/contracts/proxy/ERC1967/ERC1967Proxy.sol";
import {RaylsAccessManagerV1} from "../../privateHub/AccessControl/RaylsAccessManagerV1.sol";
import {ProgrammabilityExecutorV1} from "../../rayls-protocol/ProgrammabilityExecutor/ProgrammabilityExecutorV1.sol";
import {SharedObjects} from "../../rayls-protocol-sdk/libraries/SharedObjects.sol";
import {Constants} from "../../rayls-protocol-sdk/Constants.sol";
import {EnygmaTokenExample} from "../../rayls-protocol/test-contracts/EnygmaTokenExample.sol";
import {MockEndpointForSecurityTest} from "../unit/mocks/MockEndpointForSecurityTest.sol";
import {MockRaylsAppTokenRegistry} from "../unit/mocks/MockRaylsAppTokenRegistry.sol";

contract ApprovedTemplateReplica {
    mapping(bytes32=>bool) public allowed;
    function approve(address target,bytes4 selector) external {
        allowed[keccak256(abi.encode(target.codehash,selector))]=true;
    }
    function check(address target,bytes4 selector) external view returns(bool) {
        return allowed[keccak256(abi.encode(target.codehash,selector))];
    }
}
contract ApplicationEffects {
    mapping(bytes32=>uint256) public byRef;
    uint256 public total;
    event Effect(bytes32 indexed refId,uint256 number);
    function record(bytes32 refId) external {
        byRef[refId]++;
        total++;
        emit Effect(refId,byRef[refId]);
    }
    function fail(bytes32) external pure { revert("CONTROLLED_APP_REVERT"); }
}
contract GuardedApplicationEffects {
    mapping(bytes32=>bool) public seen;
    mapping(bytes32=>uint256) public byRef;
    uint256 public total;
    event Effect(bytes32 indexed refId,uint256 number);
    function recordOnce(bytes32 refId) external {
        if(seen[refId]) return;
        seen[refId]=true;
        byRef[refId]++;
        total++;
        emit Effect(refId,byRef[refId]);
    }
}
contract EnygmaRecoveryMechanismTest is Test {
    RaylsAccessManagerV1 manager;
    MockEndpointForSecurityTest endpoint;
    EnygmaTokenExample token;
    ProgrammabilityExecutorV1 executor;
    ApprovedTemplateReplica replica;
    ApplicationEffects app;
    GuardedApplicationEffects guarded;
    address relayer=makeAddr("research-relayer");
    address receiver=makeAddr("recipient-a");
    bytes32 constant RID=bytes32(uint256(1));
    bytes32 constant REF=keccak256("enygma-ref-A");
    uint256 constant AMT=13 ether;
    uint64 role;

    function setUp() public {
        manager=RaylsAccessManagerV1(address(new ERC1967Proxy(
          address(new RaylsAccessManagerV1()),
          abi.encodeCall(RaylsAccessManagerV1.initialize,(address(this)))
        )));
        role=manager.registerRole("RELAYER");
        manager.registerRole("MESSAGE_EXECUTOR");
        manager.grantRole(role,relayer,0);
        endpoint=new MockEndpointForSecurityTest(12346,1337);
        endpoint.setAuthority(address(manager));
        endpoint.setTrustedExecutor(address(this));
        MockRaylsAppTokenRegistry registry=new MockRaylsAppTokenRegistry();
        endpoint.registerResourceId(Constants.RESOURCE_ID_TOKEN_REGISTRY,address(registry));
        token=new EnygmaTokenExample("EnygmaResearch","ERX",address(endpoint));
        vm.prank(address(registry));
        token.setResourceId(RID);
        endpoint.registerResourceId(RID,address(token));
        replica=new ApprovedTemplateReplica();
        app=new ApplicationEffects();
        guarded=new GuardedApplicationEffects();
        executor=ProgrammabilityExecutorV1(address(new ERC1967Proxy(
          address(new ProgrammabilityExecutorV1()),
          abi.encodeCall(ProgrammabilityExecutorV1.initialize,
            (address(endpoint),address(replica),address(manager)))
        )));
        bytes4[] memory sels=new bytes4[](1);
        sels[0]=bytes4(keccak256("executeProgramData((bytes32,address,bytes4,bytes)[],uint256,address)"));
        uint64[] memory roles=new uint64[](1);
        roles[0]=role;
        manager.addFunctionAllowedRoles(address(executor),sels,roles);
        manager.grantRole(role,address(executor),0);
        replica.approve(address(token),token.crossMintStandard.selector);
        replica.approve(address(app),app.record.selector);
        replica.approve(address(app),app.fail.selector);
        replica.approve(address(guarded),guarded.recordOnce.selector);
    }

    function program(bytes32 ref,bool withApp,bool failing)
      internal view returns(SharedObjects.EnygmaProgramData[] memory steps)
    {
        steps=new SharedObjects.EnygmaProgramData[](withApp?2:1);
        steps[0]=SharedObjects.EnygmaProgramData({
            resourceId:RID,contractAddress:address(0),
            selector:token.crossMintStandard.selector,
            args:abi.encode(receiver,AMT,ref)
        });
        if(withApp)steps[1]=SharedObjects.EnygmaProgramData({
            resourceId:bytes32(0),contractAddress:address(app),
            selector:failing?app.fail.selector:app.record.selector,
            args:abi.encode(ref)
        });
    }
    function dispatch(SharedObjects.EnygmaProgramData[] memory steps) internal {
        vm.prank(relayer);
        executor.executeProgramData(steps,AMT,relayer);
    }
    function test_01_singleControl() public {
        dispatch(program(REF,true,false));
        assertEq(token.balanceOf(receiver),AMT);
        assertEq(token.totalSupply(),AMT);
        assertEq(app.byRef(REF),1);
    }
    function test_02_duplicateMintOnlyRemainsSingle() public {
        SharedObjects.EnygmaProgramData[] memory steps=program(REF,false,false);
        dispatch(steps); dispatch(steps);
        assertEq(token.balanceOf(receiver),AMT);
        assertEq(token.totalSupply(),AMT);
        assertEq(app.total(),0);
    }
    function test_03_secondAuthorizedWholeProgramRepeatsAppEffect() public {
        SharedObjects.EnygmaProgramData[] memory steps=program(REF,true,false);
        dispatch(steps); dispatch(steps);
        assertEq(token.balanceOf(receiver),AMT);
        assertEq(token.totalSupply(),AMT);
        assertEq(app.byRef(REF),2);
    }
    function test_04_revertedApplicationRollsBackSettlement() public {
        vm.expectRevert();
        dispatch(program(REF,true,true));
        assertEq(token.balanceOf(receiver),0);
        assertEq(token.totalSupply(),0);
        assertEq(app.total(),0);
        assertEq(uint256(token.referenceIdStatus(REF)),0);
    }
    function test_05_distinctReferenceStillWorks() public {
        dispatch(program(REF,true,false));
        bytes32 other=keccak256("enygma-ref-B");
        dispatch(program(other,true,false));
        assertEq(token.balanceOf(receiver),2*AMT);
        assertEq(app.byRef(REF),1);
        assertEq(app.byRef(other),1);
    }    function test_06_applicationLevelGuardSuppressesRepeatedSideEffect() public {
        SharedObjects.EnygmaProgramData[] memory steps=new SharedObjects.EnygmaProgramData[](2);
        steps[0]=SharedObjects.EnygmaProgramData({
            resourceId:RID,contractAddress:address(0),
            selector:token.crossMintStandard.selector,args:abi.encode(receiver,AMT,REF)
        });
        steps[1]=SharedObjects.EnygmaProgramData({
            resourceId:bytes32(0),contractAddress:address(guarded),
            selector:guarded.recordOnce.selector,args:abi.encode(REF)
        });
        dispatch(steps); dispatch(steps);
        assertEq(token.balanceOf(receiver),AMT);
        assertEq(token.totalSupply(),AMT);
        assertEq(guarded.byRef(REF),1);
        assertEq(guarded.total(),1);
        assertTrue(guarded.seen(REF));
    }

}
