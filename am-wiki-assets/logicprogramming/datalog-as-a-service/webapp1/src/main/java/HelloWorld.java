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
    private String kb;
    private String kb_epoch;
	private DatalogEngine en;
    private String qq;
	private int kb_sz;

    public void init() throws ServletException {
        System.out.println("INFO init()");
        kb = ""; // "Hello World";
    }

    private synchronized void start_en(String kba_, boolean append) throws DatalogParseException,DatalogValidationException {
        //assert rd != null;
        // kb = kb_; too early!
        System.out.println("INFO start_en() - new kb, size of text = " + kba_.length() + " append = "+append);
        String xtra = kb.endsWith("\n") ? "" : "\n";
		String kb_ = append ? kb + xtra + kba_ : kba_;
		
		DatalogTokenizer tk = new DatalogTokenizer(new StringReader(kb_));
        Set<Clause> prog = DatalogParser.parseProgram(tk);
        System.out.println("INFO start_en() - new kb, size of compiled items = " + prog.size());
        // AcbDatalog: You can choose what sort of engine you want here.
        DatalogEngine neweng = SemiNaiveEngine.newEngine();
        neweng.init(prog);
		// the new values en, kb and kb_sz are (re)assigned only of the text was parsed successfully.
		// if not, the previous kb remains.
        en = neweng;
        kb = kb_;
		kb_sz = prog.size();
		kb_epoch = Instant.now().toString();
        System.out.println("INFO start_en() - done.");
    }

    private synchronized List<String> run_query(String qs) throws DatalogParseException {
        qq = qs;
        DatalogTokenizer tk = new DatalogTokenizer(new StringReader(qs));
        PositiveAtom qa = DatalogParser.parseQuery(tk);
        assert en != null;
        assert qa != null;
        Set<PositiveAtom> results = en.query(qa);
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
						if(false) System.out.println("INFO doPost() kb ===\n" + kb_ + "\n===\n");
						if(kb_!=null) {
							start_en(kb_,uc.equals("learnmore"));
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
				 if(en == null) {
					jo.put("uc", uc);
					jo.put("ans", 0);
					rc = 204;
					setRetMsg(jo,"no KB.");
				 } else {
					rc = 200;
					jo.put("uc", uc);
					jo.put("ans_kb_text_sz", kb.length());
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
             if(en != null) {
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
		out.println(jo);
		System.out.println("INFO doGet() - http request completed for uc=" + uc);
		return;		

	}

		/*public void service(ServletRequest request, ServletResponse response) throws ServletException, IOException {
				System.out.println("INFO - service() called.");
		}*/
		
// sample q:
// tc(X, Y)?

//    String kb = request.getParameter("kb");
// https://stackoverflow.com/questions/63150/whats-the-best-way-to-build-a-string-of-delimited-items-in-java


    

    public void destroy() {
        // do nothing.
    }
}
