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
         DependsOn = VPC,
         Tags=Tags(
            Application=ref_stack_id,
            Name="ClientInternetGateway"),
            ))

InternetGatewayAttachment = t.add_resource(
    VPCGatewayAttachment("InternetGatewayAttachment",
                            DependsOn = InternetGateway,
                            VpcId = Ref(VPC),
                            InternetGatewayId = Ref(InternetGateway),
                         ))
ClientRouteTable = t.add_resource(
    RouteTable("ClientRouteTable",
               DependsOn = InternetGateway,
               VpcId = Ref(VPC),
                Tags=Tags(
                     Application=ref_stack_id,
                     Name="ClientRouteTable"),
               ))


ClientRouteInternetAccess = t.add_resource(
    Route("ClientRouteInternetAccess",
           DependsOn = InternetGateway,
           DestinationCidrBlock = "0.0.0.0/0",
           RouteTableId = Ref(ClientRouteTable),
           GatewayId = Ref(InternetGateway),
    )
)


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

# Client1SubnetRouteTable = t.add_resource(
#     SubnetRouteTableAssociation('Client1SubnetRouteTable',
#                                 RouteTableId = Ref(RouteTable),
#                                 SubnetId = Ref(Client1Subnet),
#     ))

Client1NetworkAcl = t.add_resource(NetworkAcl("Client1NetworkAcl",
                                              VpcId = Ref(VPC),
                                              ))

Client1NetworkAclRules = t.add_resource(NetworkAclEntry("Client1NetworkAcl",
                                                        NetworkAclId = Ref(Client1NetworkAcl),
                                                        RuleNumber = ))

Client2Subnet = t.add_resource(
    Subnet(
        'Client2Subnet',
        CidrBlock='10.62.2.0/24',
        VpcId=Ref(VPC),
        Tags=Tags(
            Application=ref_stack_id,
            Name="Client2Subnet")))

Client3Subnet = t.add_resource(
    Subnet(
        'Client3Subnet',
        CidrBlock='10.62.3.0/24',
        VpcId=Ref(VPC),
        Tags=Tags(
            Application=ref_stack_id,
            Name="Client3Subnet")))

t.add_output([
    Output(
        "VpcId",
        Description="InstanceId of the newly created EC2 instance",
        Value=Ref(VPC),
    )
])

print(t.to_yaml())
