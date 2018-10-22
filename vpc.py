from troposphere import FindInMap, GetAtt, Join
from troposphere import Parameter, Output, Ref, Select, Tags, Template, ImportValue
import troposphere.ec2 as ec2
from troposphere.ec2 import PortRange, NetworkAcl, Route, \
    VPCGatewayAttachment, SubnetRouteTableAssociation, Subnet, RouteTable, \
    VPC, NetworkInterfaceProperty, NetworkAclEntry, \
    SubnetNetworkAclAssociation, EIP, Instance, InternetGateway, \
    SecurityGroupRule, SecurityGroup, VPCDHCPOptionsAssociation

t = Template()

# may be used as a region mapping

keyname_param = t.add_parameter(Parameter(
    "RegionNumber",
    Description="Second Octet for Customer VPC",
    Type="String",
))

ref_stack_id = Ref('AWS::StackId')

VPC = t.add_resource(
    VPC(
        'VPC',
        CidrBlock='10.62.0.0/16',
        Tags=Tags(
            Application=ref_stack_id,
            Name="ClientVpc")))

# DHCPAssociation = t.add_resource(VPCDHCPOptionsAssociation("DHCPAssociation",
#     VpcId = Ref(VPC),
#     DhcpOptionsId = ImportValue("CoatesDhcp"),
# ))

InternetGateway = t.add_resource(
    InternetGateway(
        "ClientInternetGateway",
        DependsOn=VPC,
        Tags=Tags(
            Application=ref_stack_id,
            Name="ClientInternetGateway"),
    ))

InternetGatewayAttachment = t.add_resource(
    VPCGatewayAttachment("InternetGatewayAttachment",
                         DependsOn=InternetGateway,
                         VpcId=Ref(VPC),
                         InternetGatewayId=Ref(InternetGateway),
                         ))
ClientRouteTable = t.add_resource(
    RouteTable("ClientRouteTable",
               DependsOn=InternetGateway,
               VpcId=Ref(VPC),
               Tags=Tags(
                   Application=ref_stack_id,
                   Name="ClientRouteTable"),
               ))

ClientRouteInternetAccess = t.add_resource(
    Route("ClientRouteInternetAccess",
          DependsOn=InternetGateway,
          DestinationCidrBlock="0.0.0.0/0",
          RouteTableId=Ref(ClientRouteTable),
          GatewayId=Ref(InternetGateway),
          ))

# Security Groups
MonitoringHostSecurityGroup = t.add_resource(SecurityGroup(
    'MonitoringHostSecurityGroup',
    GroupDescription="MonitoringHostSecurityGroup",
    DependsOn=VPC,
    SecurityGroupIngress=[
        SecurityGroupRule(
            IpProtocol='tcp',
            FromPort='9101',
            ToPort='9101',
            CidrIp='10.62.0.0/16'
        ),
        SecurityGroupRule(
            IpProtocol='tcp',
            FromPort='8301',
            ToPort='8301',
            CidrIp='10.62.0.0/16'
        ),
        SecurityGroupRule(
            IpProtocol='udp',
            FromPort='8301',
            ToPort='8301',
            CidrIp='10.62.0.0/16'
        ),
        SecurityGroupRule(
            IpProtocol='tcp',
            FromPort='9100',
            ToPort='9100',
            CidrIp='10.62.0.0/16'
        ),
        SecurityGroupRule(
            IpProtocol='tcp',
            FromPort='9102',
            ToPort='9102',
            CidrIp='10.62.0.0/16'
        )
    ],
    VpcId=Ref(VPC),
    Tags=Tags(
        Application=ref_stack_id,
        Name="MonitoringHostSecurityGroup"),
))
CommonSecurityGroup = t.add_resource(SecurityGroup(
    'CommonSecurityGroup',
    GroupDescription="CommonSecurityGroup",
    SecurityGroupIngress=[
        SecurityGroupRule(
            IpProtocol='tcp',
            FromPort='22',
            ToPort='22',
            CidrIp='0.0.0.0/0'
        )

    ],
    VpcId=Ref(VPC),
    Tags=Tags(
        Application=ref_stack_id,
        Name="CommonSecurityGroup"),
))
HQSecurityGroup = t.add_resource(SecurityGroup(
    'HQSecurityGroup',
    GroupDescription="HQSecurityGroup",
    SecurityGroupIngress=[
        SecurityGroupRule(
            IpProtocol='tcp',
            FromPort='80',
            ToPort='80',
            CidrIp='0.0.0.0/0'
        ),
        SecurityGroupRule(
            IpProtocol='tcp',
            FromPort='443',
            ToPort='443',
            CidrIp='0.0.0.0/0'
        ),
        SecurityGroupRule(
            IpProtocol='udp',
            FromPort='1194',
            ToPort='1194',
            CidrIp='0.0.0.0/0'
        )
    ],
    VpcId=Ref(VPC),
    Tags=Tags(
        Application=ref_stack_id,
        Name="HQSecurityGroup"),
))

RancherHostSecurityGroup = t.add_resource(SecurityGroup(
    'RancherHostSecurityGroup',
    GroupDescription="RancherHostSecurityGroup",
    SecurityGroupIngress=[
        SecurityGroupRule(
            IpProtocol='udp',
            FromPort='4500',
            ToPort='4500',
            CidrIp='10.62.0.0/16'
        ),
        SecurityGroupRule(
            IpProtocol='tcp',
            FromPort='443',
            ToPort='443',
            CidrIp='0.0.0.0/0'
        ),
        SecurityGroupRule(
            IpProtocol='udp',
            FromPort='1194',
            ToPort='1194',
            CidrIp='0.0.0.0/0'
        )
    ],
    VpcId=Ref(VPC),
    Tags=Tags(
        Application=ref_stack_id,
        Name="RancherHostSecurityGroup"),
))
NFSSecurityGroup = t.add_resource(SecurityGroup(
    'NFSSecurityGroup',
    GroupDescription="NFSSecurityGroup",
    SecurityGroupIngress=[
        SecurityGroupRule(
            IpProtocol='tcp',
            FromPort='2049',
            ToPort='2049',
            CidrIp='10.62.0.0/16'
        ),
        SecurityGroupRule(
            IpProtocol='udp',
            FromPort='2049',
            ToPort='2049',
            CidrIp='10.62.0.0/16'
        ),
        SecurityGroupRule(
            IpProtocol='tcp',
            FromPort='111',
            ToPort='111',
            CidrIp='10.62.0.0/16'
        ),
        SecurityGroupRule(
            IpProtocol='udp',
            FromPort='111',
            ToPort='111',
            CidrIp='10.62.0.0/16'
        )
    ],
    VpcId=Ref(VPC),
    Tags=Tags(
        Application=ref_stack_id,
        Name="NFSSecurityGroup"),
))

Client1Subnet = t.add_resource(
    Subnet(
        'Client1Subnet',
        CidrBlock='10.62.1.0/24',
        VpcId=Ref(VPC),
        Tags=Tags(
            Application=ref_stack_id,
            Name="Client1Subnet")))

Client1SubnetAssociation = t.add_resource(SubnetRouteTableAssociation
                                          ("Client1SubnetAssociation",
                                           SubnetId=Ref(Client1Subnet),
                                           RouteTableId=Ref(ClientRouteTable)))

Client1NetworkAcl = t.add_resource(NetworkAcl("Client1NetworkAcl",
                                              VpcId=Ref(VPC),
                                              ))

Client1NetworkAclAssociation = t.add_resource(SubnetNetworkAclAssociation
                                             ("Client1NetworkAclAssociation",
                                              NetworkAclId=Ref(Client1NetworkAcl),
                                              SubnetId=Ref(Client1Subnet)))

Client1NetworkAclInboundAllowSubnet = t.add_resource(NetworkAclEntry
                                                     ("Client1NetworkAclInboundAllowSubnet",
                                                      NetworkAclId=Ref(Client1NetworkAcl),
                                                      RuleNumber=100,
                                                      CidrBlock="10.62.1.0/24",
                                                      RuleAction="allow",
                                                      PortRange=PortRange(To="-1", From="-1"),
                                                      Protocol="-1",
                                                      Egress="false",
                                                      ))
Client1NetworkAclInbooundDenyVpc = t.add_resource(NetworkAclEntry
                                                  ("Client1NetworkAclInboundDenyVpc",
                                                   NetworkAclId=Ref(Client1NetworkAcl),
                                                   RuleNumber=110,
                                                   CidrBlock="10.62.0.0/16",
                                                   RuleAction="deny",
                                                   PortRange=PortRange(To="-1", From="-1"),
                                                   Protocol="-1",
                                                   Egress="false",
                                                   ))
Client1NetworkAclInboundAllowAll = t.add_resource(NetworkAclEntry
                                                  ("Client1NetworkAclInboundAllowAll",
                                                   NetworkAclId=Ref(Client1NetworkAcl),
                                                   RuleNumber=120,
                                                   CidrBlock="0.0.0.0/0",
                                                   RuleAction="allow",
                                                   PortRange=PortRange(To="-1", From="-1"),
                                                   Protocol="-1",
                                                   Egress="false",
                                                   ))
Client1NetworkAclOutboundAllowSubnet = t.add_resource(NetworkAclEntry
                                                      ("Client1NetworkAclOutboundAllowSubnet",
                                                       NetworkAclId=Ref(Client1NetworkAcl),
                                                       RuleNumber=100,
                                                       CidrBlock="10.62.1.0/24",
                                                       RuleAction="allow",
                                                       PortRange=PortRange(To="-1", From="-1"),
                                                       Protocol="-1",
                                                       Egress="true",
                                                       ))
Client1NetworkAclOutboundDenyVpc = t.add_resource(NetworkAclEntry
                                                  ("Client1NetworkAclOutboundDenyVpc",
                                                   NetworkAclId=Ref(Client1NetworkAcl),
                                                   RuleNumber=110,
                                                   CidrBlock="10.62.0.0/16",
                                                   RuleAction="deny",
                                                   PortRange=PortRange(To="-1", From="-1"),
                                                   Protocol="-1",
                                                   Egress="true",
                                                   ))
Client1NetworkAclOutboundAllowAll = t.add_resource(NetworkAclEntry
                                                   ("Client1NetworkAclOutboundAllowAll",
                                                    NetworkAclId=Ref(Client1NetworkAcl),
                                                    RuleNumber=120,
                                                    CidrBlock="0.0.0.0/0",
                                                    RuleAction="allow",
                                                    PortRange=PortRange(To="-1", From="-1"),
                                                    Protocol="-1",
                                                    Egress="true",
                                                    ))
Client2Subnet = t.add_resource(
    Subnet(
        'Client2Subnet',
        CidrBlock='10.62.2.0/24',
        VpcId=Ref(VPC),
        Tags=Tags(
            Application=ref_stack_id,
            Name="Client2Subnet")))

Client2NetworkAcl = t.add_resource(NetworkAcl("Client2NetworkAcl",
                                              VpcId=Ref(VPC),
                                              ))

Client2SubnetAssociation = t.add_resource(SubnetRouteTableAssociation
                                          ("Client2SubnetAssociation",
                                           SubnetId=Ref(Client2Subnet),
                                           RouteTableId=Ref(ClientRouteTable)))

Client2NetworkAclAssociation = t.add_resource(SubnetNetworkAclAssociation
                                             ("Client2NetworkAclAssociation",
                                              NetworkAclId=Ref(Client2NetworkAcl),
                                              SubnetId=Ref(Client2Subnet)))

Client2NetworkAclInboundAllowSubnet = t.add_resource(NetworkAclEntry
                                                     ("Client2NetworkAclInboundAllowSubnet",
                                                      NetworkAclId=Ref(Client2NetworkAcl),
                                                      RuleNumber=100,
                                                      CidrBlock="10.62.2.0/24",
                                                      RuleAction="allow",
                                                      PortRange=PortRange(To="-1", From="-1"),
                                                      Protocol="-1",
                                                      Egress="false",
                                                      ))
Client2NetworkAclInbooundDenyVpc = t.add_resource(NetworkAclEntry
                                                  ("Client2NetworkAclInboundDenyVpc",
                                                   NetworkAclId=Ref(Client2NetworkAcl),
                                                   RuleNumber=110,
                                                   CidrBlock="10.62.0.0/16",
                                                   RuleAction="deny",
                                                   PortRange=PortRange(To="-1", From="-1"),
                                                   Protocol="-1",
                                                   Egress="false",
                                                   ))
Client2NetworkAclInboundAllowAll = t.add_resource(NetworkAclEntry
                                                  ("Client2NetworkAclInboundAllowAll",
                                                   NetworkAclId=Ref(Client2NetworkAcl),
                                                   RuleNumber=120,
                                                   CidrBlock="0.0.0.0/0",
                                                   RuleAction="allow",
                                                   PortRange=PortRange(To="-1", From="-1"),
                                                   Protocol="-1",
                                                   Egress="false",
                                                   ))
Client2NetworkAclOutboundAllowSubnet = t.add_resource(NetworkAclEntry
                                                      ("Client2NetworkAclOutboundAllowSubnet",
                                                       NetworkAclId=Ref(Client2NetworkAcl),
                                                       RuleNumber=100,
                                                       CidrBlock="10.62.2.0/24",
                                                       RuleAction="allow",
                                                       PortRange=PortRange(To="-1", From="-1"),
                                                       Protocol="-1",
                                                       Egress="true",
                                                       ))
Client2NetworkAclOutboundDenyVpc = t.add_resource(NetworkAclEntry
                                                  ("Client2NetworkAclOutboundDenyVpc",
                                                   NetworkAclId=Ref(Client2NetworkAcl),
                                                   RuleNumber=110,
                                                   CidrBlock="10.62.0.0/16",
                                                   RuleAction="deny",
                                                   PortRange=PortRange(To="-1", From="-1"),
                                                   Protocol="-1",
                                                   Egress="true",
                                                   ))
Client2NetworkAclOutboundAllowAll = t.add_resource(NetworkAclEntry
                                                   ("Client2NetworkAclOutboundAllowAll",
                                                    NetworkAclId=Ref(Client2NetworkAcl),
                                                    RuleNumber=120,
                                                    CidrBlock="0.0.0.0/0",
                                                    RuleAction="allow",
                                                    PortRange=PortRange(To="-1", From="-1"),
                                                    Protocol="-1",
                                                    Egress="true",
                                                    ))

Client3Subnet = t.add_resource(
    Subnet(
        'Client3Subnet',
        CidrBlock='10.62.3.0/24',
        VpcId=Ref(VPC),
        Tags=Tags(
            Application=ref_stack_id,
            Name="Client3Subnet")))

Client3SubnetAssociation = t.add_resource(SubnetRouteTableAssociation
                                          ("Client3SubnetAssociation",
                                           SubnetId=Ref(Client3Subnet),
                                           RouteTableId=Ref(ClientRouteTable)))

Client3NetworkAcl = t.add_resource(NetworkAcl("Client3NetworkAcl",
                                              VpcId=Ref(VPC),
                                              ))


Client3NetworkAclAssociation = t.add_resource(SubnetNetworkAclAssociation
                                             ("Client3NetworkAclAssociation",
                                              NetworkAclId=Ref(Client3NetworkAcl),
                                              SubnetId=Ref(Client3Subnet)))

Client3NetworkAclInboundAllowSubnet = t.add_resource(NetworkAclEntry
                                                     ("Client3NetworkAclInboundAllowSubnet",
                                                      NetworkAclId=Ref(Client3NetworkAcl),
                                                      RuleNumber=100,
                                                      CidrBlock="10.62.3.0/24",
                                                      RuleAction="allow",
                                                      PortRange=PortRange(To="-1", From="-1"),
                                                      Protocol="-1",
                                                      Egress="false",
                                                      ))
Client3NetworkAclInbooundDenyVpc = t.add_resource(NetworkAclEntry
                                                  ("Client3NetworkAclInboundDenyVpc",
                                                   NetworkAclId=Ref(Client3NetworkAcl),
                                                   RuleNumber=110,
                                                   CidrBlock="10.62.0.0/16",
                                                   RuleAction="deny",
                                                   PortRange=PortRange(To="-1", From="-1"),
                                                   Protocol="-1",
                                                   Egress="false",
                                                   ))
Client3NetworkAclInboundAllowAll = t.add_resource(NetworkAclEntry
                                                  ("Client3NetworkAclInboundAllowAll",
                                                   NetworkAclId=Ref(Client3NetworkAcl),
                                                   RuleNumber=120,
                                                   CidrBlock="0.0.0.0/0",
                                                   RuleAction="allow",
                                                   PortRange=PortRange(To="-1", From="-1"),
                                                   Protocol="-1",
                                                   Egress="false",
                                                   ))
Client3NetworkAclOutboundAllowSubnet = t.add_resource(NetworkAclEntry
                                                      ("Client3NetworkAclOutboundAllowSubnet",
                                                       NetworkAclId=Ref(Client3NetworkAcl),
                                                       RuleNumber=100,
                                                       CidrBlock="10.62.3.0/24",
                                                       RuleAction="allow",
                                                       PortRange=PortRange(To="-1", From="-1"),
                                                       Protocol="-1",
                                                       Egress="true",
                                                       ))
Client3NetworkAclOutboundDenyVpc = t.add_resource(NetworkAclEntry
                                                  ("Client3NetworkAclOutboundDenyVpc",
                                                   NetworkAclId=Ref(Client3NetworkAcl),
                                                   RuleNumber=110,
                                                   CidrBlock="10.62.0.0/16",
                                                   RuleAction="deny",
                                                   PortRange=PortRange(To="-1", From="-1"),
                                                   Protocol="-1",
                                                   Egress="true",
                                                   ))
Client3NetworkAclOutboundAllowAll = t.add_resource(NetworkAclEntry
                                                   ("Client3NetworkAclOutboundAllowAll",
                                                    NetworkAclId=Ref(Client3NetworkAcl),
                                                    RuleNumber=120,
                                                    CidrBlock="0.0.0.0/0",
                                                    RuleAction="allow",
                                                    PortRange=PortRange(To="-1", From="-1"),
                                                    Protocol="-1",
                                                    Egress="true",
                                                    ))

t.add_output([
    Output(
        "VpcId",
        Description="InstanceId of the newly created EC2 instance",
        Value=Ref(VPC),
    )
])

print(t.to_yaml())
