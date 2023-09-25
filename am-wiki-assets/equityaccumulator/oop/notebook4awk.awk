# notebook4awk.awk

/#GLUERAY_DOCOMMENT_BEGIN/ { print; GLUERAY_DOCOMMENT=1; next}
/#GLUERAY_DOCOMMENT_END/   { print; GLUERAY_DOCOMMENT=0; next}
/#GLUERAY_UNCOMMENT_BEGIN/ { print; GLUERAY_UNCOMMENT=1; next}
/#GLUERAY_UNCOMMENT_END/   { print; GLUERAY_UNCOMMENT=0; next}

function get_line_with_the_first_hash_removed(L) {
    x=index(L,"#")
	L2=substr(L, 1, x-1) substr(L, x+1)
    return x==0 ? L : L2
}

function get_line_with_a_hash_in_front(L) {
    return "#" L
}

GLUERAY_DOCOMMENT==1 { print get_line_with_a_hash_in_front($0); next}
GLUERAY_UNCOMMENT==1 { print get_line_with_the_first_hash_removed($0); next }

{print}