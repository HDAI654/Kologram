sh run_tests.sh auth_service/ test/
echo "============================================="
echo "============================================="
cd chat_service/test
go test -v ./...
cd -
echo "============================================="
echo "============================================="
sh run_tests.sh market_service/ test/
echo "============================================="
echo "============================================="
sh run_tests.sh notification_dispatcher/ test/