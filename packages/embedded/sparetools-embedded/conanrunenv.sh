script_folder="/home/sparrow/projects/dev-tools/sparetools/packages/embedded/sparetools-embedded"
echo "echo Restoring environment" > "$script_folder/deactivate_conanrunenv.sh"
for v in 
do
    is_defined="true"
    value=$(printenv $v) || is_defined="" || true
    if [ -n "$value" ] || [ -n "$is_defined" ]
    then
        echo export "$v='$value'" >> "$script_folder/deactivate_conanrunenv.sh"
    else
        echo unset $v >> "$script_folder/deactivate_conanrunenv.sh"
    fi
done

