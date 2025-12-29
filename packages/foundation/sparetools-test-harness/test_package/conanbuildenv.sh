script_folder="/home/sparrow/projects/dev-tools/sparetools/packages/foundation/sparetools-test-harness/test_package"
echo "echo Restoring environment" > "$script_folder/deactivate_conanbuildenv.sh"
for v in 
do
    is_defined="true"
    value=$(printenv $v) || is_defined="" || true
    if [ -n "$value" ] || [ -n "$is_defined" ]
    then
        echo export "$v='$value'" >> "$script_folder/deactivate_conanbuildenv.sh"
    else
        echo unset $v >> "$script_folder/deactivate_conanbuildenv.sh"
    fi
done

