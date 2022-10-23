clear
rm -f test-out/*.bin

echo "=== Default settings ==="
python3 corruptor.py test.bin test-out/default.bin
diff \
    <(od -Ax -tx1 -v -w1 test.bin) \
    <(od -Ax -tx1 -v -w1 test-out/default.bin) | grep "^[<>]"
echo

echo "=== Flip 1 bit in 4 bytes ==="
python3 corruptor.py -mf -c4 test.bin test-out/flip.bin
diff \
    <(od -Ax -tx1 -v -w1 test.bin) \
    <(od -Ax -tx1 -v -w1 test-out/flip.bin) | grep "^[<>]"
echo

echo "=== Invert all bits in 4 bytes, verbose ==="
python3 corruptor.py -mi -c4 -v test.bin test-out/invert.bin
diff \
    <(od -Ax -tx1 -v -w1 test.bin) \
    <(od -Ax -tx1 -v -w1 test-out/invert.bin) | grep "^[<>]"
echo

echo "=== Add/subtract 1 in last 4 bytes ==="
python3 corruptor.py -ma -c4 -s252 test.bin test-out/addsub.bin
diff \
    <(od -Ax -tx1 -v -w1 test.bin) \
    <(od -Ax -tx1 -v -w1 test-out/addsub.bin) | grep "^[<>]"
echo

echo "=== Randomize 4 bytes between 0x0080-0x008f ==="
python3 corruptor.py -mr -c4 -s128 -l16 test.bin test-out/randomize.bin
diff \
    <(od -Ax -tx1 -v -w1 test.bin) \
    <(od -Ax -tx1 -v -w1 test-out/randomize.bin) | grep "^[<>]"
echo

echo "=== These should cause four errors ==="
python3 corruptor.py -s256 test.bin test-out/dummy1.bin
python3 corruptor.py -l257 test.bin test-out/dummy2.bin
python3 corruptor.py -s255 -l2 test.bin test-out/dummy3.bin
python3 corruptor.py -c2 -s255 test.bin test-out/dummy4.bin
echo
