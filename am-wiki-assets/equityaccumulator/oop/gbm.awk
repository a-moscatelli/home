# this is gbm.awk
# type gbm.py | gawk.exe -f gbm.awk > gbm-for-glueray.py
# https://www.gnu.org/software/gawk/manual/html_node/String-Functions.html

{
	theprefix="#(AWSGLUERAY_ONLY)"
	x=index($0,theprefix)
	notfound=(x==0)
	if(notfound) {
		print
	} else {
		# replacing {theprefix} with nothing 
		line_before_theprefix = substr($0,1,x-1)
		line_after_theprefix = substr($0,x+length(theprefix))
		print line_before_theprefix line_after_theprefix
	}
}