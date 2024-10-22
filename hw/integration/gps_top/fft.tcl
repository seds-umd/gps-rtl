# From: https://grittyengineer.com/creating-vivado-ip-the-smart-tcl-way/

# Check IP
if { [file isdirectory "IP/XilinxFFT"] } {
    # if the IP files exist, we already generated the IP, so we can just
    # read the ip definition (.xci)
    read_ip IP/XilinxFFT/XilinxFFT.xci
} else {
    # IP folder does not exist. Create IP folder
    file mkdir IP

    # create_ip requires that a project is open in memory. Create project 
    # but don't do anything with it
    # create_project -in_memory

    # paste commands from Journal file to recreate IP
    create_ip -name xfft -vendor xilinx.com -library ip -version 9.1 -module_name XilinxFFT -dir IP

    set_property -dict [list \
        CONFIG.transform_length {4096} \
        CONFIG.target_clock_frequency {100} \
        CONFIG.implementation_options {radix_4_burst_io} \
        CONFIG.input_width {8} \
        CONFIG.phase_factor_width {10} \
        CONFIG.scaling_options {block_floating_point} \
        CONFIG.rounding_modes {convergent_rounding} \
        CONFIG.aclken {true} \
        CONFIG.aresetn {true} \
        CONFIG.output_ordering {natural_order} \
        CONFIG.number_of_stages_using_block_ram_for_data_and_phase_factors {0} \
    ] [get_ips XilinxFFT]

    generate_target all [get_ips]

    # Synthesize all the IP
    synth_ip [get_ips]
}
