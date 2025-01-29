"""This profile uses 2 switches and 4 hosts. 
2 switches will have 2 hosts each and 2 links to connect the switches."""

# Import the Portal object.
import geni.portal as portal

# Import the ProtoGENI library.
import geni.rspec.pg as pg

# Import the Emulab specific extensions.
import geni.rspec.emulab as emulab


class GLOBALS:
    image = "urn:publicid:IDN+emulab.net+image+emulab-ops//UBUNTU22-64-STD"
    base_ip = "192.168.1."
    netmask = "255.255.255.0"


pc = portal.Context()
request = pc.makeRequestRSpec()

# Read parameters.
pc.defineParameter("nr_nodes", "Number of nodes", portal.ParameterType.INTEGER, 4)
pc.defineParameter(
    "phystype0",
    "Switch 0 type",
    portal.ParameterType.STRING,
    "dell-s4048",
    [("mlnx-sn2410", "Mellanox SN2410"), ("dell-s4048", "Dell S4048")],
)

pc.defineParameter(
    "phystype1",
    "Switch 1 type",
    portal.ParameterType.STRING,
    "dell-s4048",
    [("mlnx-sn2410", "Mellanox SN2410"), ("dell-s4048", "Dell S4048")],
)

pc.defineParameter("user", "User", portal.ParameterType.STRING, "kwzhao")
pc.defineParameter("branch", "emu branch", portal.ParameterType.STRING, "main")

# Retrieve the values the user specifies during instantiation. Must be called exactly once.
params = pc.bindParameters()

# Create nodes
nodes = []
for i in range(params.nr_nodes):
    node = request.RawPC(f"node{i}")
    node.hardware_type = "xl170"
    node.disk_image = GLOBALS.image

    iface = node.addInterface()

    ip_address = GLOBALS.base_ip + str(i)
    iface.addAddress(pg.IPv4Address(ip_address, GLOBALS.netmask))
    nodes.append((node, iface))

    # Add a startup script.
    if i == 0:
        # The first node is the manager.
        worker_ips = " ".join(
            [GLOBALS.base_ip + str(j) for j in range(0, params.nr_nodes)]
        )
        command = "/local/repository/setup-manager.sh {} {}".format(
            params.branch, worker_ips
        )
    else:
        # All the rest are workers.
        command = "/local/repository/setup-worker.sh {} {} {} {}".format(
            params.branch, i, ip_address, GLOBALS.base_ip + "0"
        )
    node.addService(
        pg.Execute(
            shell="bash", command="sudo -u {} -H {}".format(params.user, command)
        )
    )

# Create switches and assign types.
switches = []
for i, swtype in enumerate([params.phystype0, params.phystype1]):
    switch = request.Switch(f"mysw{i}")
    switch.hardware_type = swtype
    switches.append(switch)

# Link hosts to switches: 2 hosts to switch 2 and 4 hosts to switch 4.
for i, (node, iface) in enumerate(nodes):
    switch = switches[0]
    if i >= 2:
        switch = switches[1]
    sw_iface = switch.addInterface()
    link = request.L1Link(f"link_node{i}_switch{0 if i < 2 else 1}")
    link.addInterface(iface)
    link.addInterface(sw_iface)

# Create trunk links between switches.
trunk_links = [(0, 1)]

# Two links per trunk.
for i, (sw1, sw2) in enumerate(trunk_links):
    sw1_iface = switches[sw1].addInterface()
    sw2_iface = switches[sw2].addInterface()
    link = request.L1Link(f"link_sw{sw1}_sw{sw2}")
    link.addInterface(sw1_iface)
    link.addInterface(sw2_iface)

# Print the RSpec to the enclosing page.
pc.printRequestRSpec(request)
