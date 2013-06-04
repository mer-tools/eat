#!/bin/sh
#
# eat-selftest - Executes all found tests

# wait before running the tests if desired
if [ "$1" != "" ]; then
	sleep $1
fi

export DISPLAY=:0

RESULTPATH=$HOME/testresults
if [ ! -d $RESULTPATH ];then
	mkdir -p $RESULTPATH
fi

for i in `ls /usr/share/*-tests/tests.xml`
do
	NAME=`echo $i | sed 's/\/usr\/share\///'`
	NAME=`echo $NAME | sed 's/\/tests.xml//'`
	testrunner-lite -f $i -o $RESULTPATH/$NAME-results.xml -v 2>&1 | tee \
	$RESULTPATH/$NAME-testlog
done

exit $?
