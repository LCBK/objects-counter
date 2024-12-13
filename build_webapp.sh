cd web_app

npm install
if [ $? -ne 0 ]; then
    echo "Failed to install npm packages"
    exit 1
fi

npm run build

echo ====================================================
echo Success, check web_app/dist folder for built files
echo
echo To serve the web app, you can use:
echo
echo \> cd web_app
echo "(if serve is not installed call 'npm install serve')"
echo \> serve -s dist
echo =====================================================
