set proj_path [lindex $argv 0]
set module_nr [lindex $argv 1]
open_project $proj_path/proj/module_$module_nr/module_$module_nr/module_$module_nr.xpr
open_run impl_1
file mkdir $proj_path/proj/module_$module_nr/products
write_bitstream -force $proj_path/proj/module_$module_nr/products/module_$module_nr.bit
