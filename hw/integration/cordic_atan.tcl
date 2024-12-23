# From: https://grittyengineer.com/creating-vivado-ip-the-smart-tcl-way/

# User guide: https://docs.amd.com/v/u/en-US/pg105-cordic

# Resource usage on K325
# 12b input, 9b output: 340 LUTs, 395 FFs
# 12b input, 11b output: 486 LUTs, 556 FFs

# Check IP
if { [file isdirectory "IP/CordicAtan"] } {
    # if the IP files exist, we already generated the IP, so we can just
    # read the ip definition (.xci)
    read_ip IP/CordicAtan/CordicAtan.xci
} else {
    # IP folder does not exist. Create IP folder
    file mkdir IP

    # create_ip requires that a project is open in memory. Create project 
    # but don't do anything with it
    # create_project -in_memory

    # paste commands from Journal file to recreate IP
    create_ip -name cordic -vendor xilinx.com -library ip -version 6.0 -module_name CordicAtan -dir IP

    set_property -dict [list \
        CONFIG.Functional_Selection {Arc_Tan} \
        CONFIG.Pipelining_Mode {Optimal} \
        CONFIG.Phase_Format {Scaled_Radians} \
        CONFIG.Input_Width {12} \
        CONFIG.Output_Width {11} \
        CONFIG.Round_Mode {Round_Pos_Neg_Inf} \
        CONFIG.flow_control {Blocking} \
        CONFIG.optimize_goal {Resources} \
        CONFIG.ACLKEN {false} \
        CONFIG.ARESETN {true} \
        CONFIG.Data_Format {SignedFraction} \
        CONFIG.cartesian_has_tuser {true} \
        CONFIG.cartesian_tuser_width {4} \
        CONFIG.out_tready {true} \
        CONFIG.coarse_rotation {true} \
    ] [get_ips CordicAtan]

    generate_target all [get_ips]

    # Synthesize all the IP
    synth_ip [get_ips]
}
