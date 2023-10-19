// https://www.tutorialspoint.com/servlets/servlets-first-example.htm

// for servlet
import java.io.*;
import javax.servlet.*;
import javax.servlet.http.*;
import java.time.Instant;

// for abcdatalog
import java.io.StringReader;
import java.util.Map;
import java.util.Set;
import java.util.List;
import java.util.LinkedList;
import edu.harvard.seas.pl.abcdatalog.engine.DatalogEngine;
import edu.harvard.seas.pl.abcdatalog.ast.PositiveAtom;
import edu.harvard.seas.pl.abcdatalog.parser.DatalogTokenizer;
import edu.harvard.seas.pl.abcdatalog.parser.DatalogParseException;
import edu.harvard.seas.pl.abcdatalog.ast.validation.DatalogValidationException;
import edu.harvard.seas.pl.abcdatalog.parser.DatalogParser;
import edu.harvard.seas.pl.abcdatalog.ast.Clause;
import edu.harvard.seas.pl.abcdatalog.engine.bottomup.sequential.SemiNaiveEngine;

// for REST
import org.json.JSONObject;
import org.json.JSONException;

// Extend HttpServlet class
public class HelloWorld extends HttpServlet {

    // STATEFUL; it is kept across requests by curl.
    private String kb_online;
    private String kb_next;
    private String kb_epoch; // of kb_next
    //private String qq; // last query - discontinued.
	private int kb_sz; // ref. kb_next
	// NB this is a concurrent system with a shared KB. concurrency APIs are needed to avoid dirty data and results.
	private DatalogEngine en_online; // used by run_query - run_query will perform an onthefly engine update before running the query if the KB is outdated.
	private DatalogEngine en_next; // used by prepare_next_engine / submitkb in synchronized mode.
	
	
	private boolean is_kb_outdated() {
		return en_next != null;
	}
	private boolean is_kb_online_or_in_queue() {
		return (en_online != null) || (en_next != null);
	}
	
	private synchronized void switch_to_latest_engine_if_outdated() {
		if(is_kb_outdated()) {
			en_online = en_next;
			en_next = null;
			kb_online = kb_next;
			kb_next = null;
			System.out.println("INFO switch_to_latest_engine_if_outdated() was done. The next engine is online.");
		}
	}

    private synchronized void prepare_next_engine(String kba_, boolean append) throws DatalogParseException,DatalogValidationException {
		// prepare_next_engine() works on kb_next only. kb_next may be empty.
		
		// called by doPost()
        //assert rd != null;
        // kb_online = kb_; too early!
        System.out.println("INFO prepare_next_engine() - new KB, size of text = " + kba_.length() + " append = "+append);
		
		if(kb_next==null) {kb_next=kb_online;}	// init() ensures that kb_online is never null.

		String xtra = kb_next.endsWith("\n") ? "" : "\n";
		kb_next = append ? kb_next + xtra + kba_ : kba_;
		
		DatalogTokenizer tk = new DatalogTokenizer(new StringReader(kb_next));
        Set<Clause> prog = DatalogParser.parseProgram(tk);
		kb_sz = prog.size();
        System.out.println("INFO prepare_next_engine() - new KB, size of compiled items = " + kb_sz);
        // AcbDatalog: You can choose what sort of engine you want here.
        en_next = SemiNaiveEngine.newEngine();
        en_next.init(prog);
		// the new values en_online, kb_online and kb_sz are (re)assigned only of the text was parsed successfully.
		// if not, the previous kb_online remains.
        //kb_next = kb_;
		kb_epoch = Instant.now().toString();
        System.out.println("INFO prepare_next_engine() - done. The next engine is offline but ready to move online.");
    }

    private synchronized List<String> run_query(String qs) throws DatalogParseException {
        //qq = qs;
        DatalogTokenizer tk = new DatalogTokenizer(new StringReader(qs));
        PositiveAtom qa = DatalogParser.parseQuery(tk);
		switch_to_latest_engine_if_outdated();
        assert en_online != null;
        assert qa != null;
        Set<PositiveAtom> results = en_online.query(qa);
        List<String> ret = new LinkedList<>();
        for (PositiveAtom result : results) {
            ret.add(result.toString());
        }
        return ret;
    }

    private String getPostParam(Map<String,String[]> postm, String postk) {
        try { return postm.get(postk)[0];} catch(Exception ex){ return null; }
        // the param is not there: null is returned. printed as "null"
        // the param is there without a value: empty string "" is returned.
    }

    private void setRetMsg(JSONObject jo,String retmsg) {
        try { jo.put("ret_msg", retmsg);} 
		catch(JSONException exj) {
		System.out.println("ERROR15 - setRetMsg - " + exj); }
    }
	
	private synchronized JSONObject getJsonPayload(BufferedReader reader) {
		// https://stackoverflow.com/questions/3831680/httpservletrequest-get-json-post-data
		StringBuffer jb = new StringBuffer();
		String line = null;
		try {
			while ((line = reader.readLine()) != null)
			jb.append(line);
		} catch (Exception e) { /*report an error*/ }
		//System.out.println("doPost() jb="+jb);	// jb=uc=learn&kb=%25+abcdatalog.input.txt%0Aisa%28h
		JSONObject jsonpayload=null;
		try {
			jsonpayload =  new JSONObject(jb.toString());// HTTP.toJSONObject(jb.toString());
		} catch (JSONException e) {
			// crash and burn
			System.out.println("json JSONException =" + e);
			//throw new IOException("Error parsing JSON request string");
		}
		return jsonpayload;
	}

	private synchronized String getPostValue(JSONObject jsonpayload, String key) {
		String uc=null;
		try { uc = jsonpayload.get(key).toString(); } catch(JSONException je) {
			System.out.println("INFO getPostValue() " + key + " = " + je);
		}
		if(uc.equals("")) uc=null;
		return uc;
	}


	// public methods:

    public void init() throws ServletException {
        System.out.println("INFO init()");
        kb_online = ""; // "Hello World";
    }

    public void doPost(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
		int rc = 501; // Not Implemented.
		System.out.println("INFO doPost() starts.");
		// https://stackoverflow.com/questions/3831680/httpservletrequest-get-json-post-data
		//request.getReader()
		BufferedReader reader = request.getReader();
		JSONObject jsonpayload = getJsonPayload(reader);
		
        PrintWriter out = response.getWriter();
        response.setContentType("application/json");
        response.setCharacterEncoding("utf-8");
        
		JSONObject jo = new JSONObject();  // https://www.baeldung.com/java-org-json
		/*
        Map<String,String[]> postm = request.getParameterMap();
        String uc = getPostParam(postm,"uc");
		String height = request.getParameter("uc");
		String fromQuery2 = request.getParameterValues("name")[0];
		String[] fromForm2 = request.getParameterValues("kb");
		*/
		
		String uc = getPostValue(jsonpayload,"uc");
		try {
			jo.put("uc", uc);
		} catch(JSONException exj) {
				System.out.println("ERROR19 - uc=" + uc + " " + exj);
				setRetMsg(jo,exj.toString());
		}
		setRetMsg(jo,"unsupported");
/* sample kb:
edge(a, b).
edge(b, c).
edge(c, d).
edge(d, c).
tc(X, Y) :- edge(X, Y).
tc(X, Y) :- tc(X, Z), tc(Z, Y).
*/

// edge(a, b). edge(b, c). edge(c, d). edge(d, c). tc(X, Y) :- edge(X, Y). tc(X, Y) :- tc(X, Z), tc(Z, Y).
		
		if(uc.equals("learn") || uc.equals("learnmore")) {  // ?uc=learn&kb=........
					rc = 400;
					try {
						String kb_ = getPostValue(jsonpayload,"kb"); // jsonpayload.get("kb").toString();
						if(false) System.out.println("INFO doPost() KB ===\n" + kb_ + "\n===\n");
						if(kb_!=null) {
							prepare_next_engine( kb_, uc.equals("learnmore"));
							setRetMsg(jo,"KB loaded");
							rc = 201;
							jo.put("KB size", kb_.length());
						} else {
							setRetMsg(jo,"KB null and not loaded.");							
						}
					} catch(JSONException exj) {
						System.out.println("ERROR17 - uc=" + uc + " " + exj);
						setRetMsg(jo,exj.toString());
					} catch(DatalogParseException ex1) {
						System.out.println("ERROR10 - uc=" + uc + " " + ex1);
						setRetMsg(jo,ex1.toString());
					} catch(DatalogValidationException ex2) {
						System.out.println("ERROR11 - uc=" + uc + " " + ex2);
						setRetMsg(jo,ex2.toString());
					} catch (Exception eee) {
						System.out.println("ERROR16 - uc=" + uc + " " + eee);
					}
        }
		response.setStatus(rc);	
		out.println(jo);
		System.out.println("INFO doPost() - http request completed for uc=" + uc);
		return;

    }

    public void doGet(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
		int rc = 501; // Not Implemented.
        PrintWriter out = response.getWriter();
        response.setContentType("application/json");
        response.setCharacterEncoding("utf-8");
		System.out.println("INFO doGet() starts.");
        //String httpmet = request.getMethod().toUpperCase(); // toUpperCase is redundant.
        //System.out.println("HTTP Method = " + httpmet);
        //assert httpmet.equals("POST");
        JSONObject jo = new JSONObject();  // https://www.baeldung.com/java-org-json
        Map<String,String[]> postm = request.getParameterMap();
        // https://docs.oracle.com/javaee/5/api/javax/servlet/ServletRequest.html#getParameter(java.lang.String)
        // The keys in the parameter map are of type String. The values in the parameter map are of type String array.

        String uc = getPostParam(postm,"uc");
		System.out.println("INFO doGet() starts with uc=" + uc);

       if(uc.equals("kb")) {  // ?uc=query&qs=........
 			rc = 400;
            try {
				if(! is_kb_online_or_in_queue()) {
					jo.put("uc", uc);
					jo.put("ans", 0);
					rc = 204;
					setRetMsg(jo,"no KB.");
				 } else {
					rc = 200;
					jo.put("uc", uc);
					jo.put("ans_kb_text_sz", kb_online.length());
					jo.put("ans_kb_sz", kb_sz);
					jo.put("ans_kb_load_epoch", kb_epoch);
					setRetMsg(jo,"valid KB.");
				 }
				} catch(JSONException exj) {
					System.out.println("ERROR12 - uc=" + uc + " " + exj);
				}
		}
 
        if(uc.equals("query")) {  // ?uc=query&qs=........
			rc = 400;
             if(is_kb_online_or_in_queue()) {
				try {
					String qq_ = getPostParam(postm,"qs");
					//String qq_ = request.getParameter("qs");
					List<String> ss = new LinkedList<>();
					ss = run_query(qq_);
					int sz = ss.size();
					jo.put("uc", uc);
					jo.put("qs", qq_);
					jo.put("ans_sz", sz);
					jo.put("ans", ss);
					setRetMsg(jo,"query executed.");
					rc = sz==0 ? 204 : 200;
				} catch(DatalogParseException exp) {
					setRetMsg(jo,exp.toString());
				} catch(JSONException exj) {
					System.out.println("ERROR13 - uc=" + uc + " " + exj);
				}
			 } else {
					setRetMsg(jo,"query not executed because no KB was loaded.");
					rc = 404; // not found
					try {
						jo.put("uc", uc);				 
					} catch(JSONException exj) {
						System.out.println("ERROR14 - uc=" + uc + " " + exj);
					}
			 }
        }
		response.setStatus(rc);
		out.println(jo);
		System.out.println("INFO doGet() - http request completed for uc=" + uc);
		return;		

	}

	/*
	KEEP THIS COMMENTED - THE SERVLET WILL HANG OTHERWISE
	public void service(ServletRequest request, ServletResponse response) throws ServletException, IOException {
			// (not called)
			System.out.println("INFO - service() called.");
	}
	*/
	
		
// sample q:
// tc(X, Y)?

//    String kb = request.getParameter("kb");
// https://stackoverflow.com/questions/63150/whats-the-best-way-to-build-a-string-of-delimited-items-in-java


    

    public void destroy() {
        // do nothing.
    }
}
