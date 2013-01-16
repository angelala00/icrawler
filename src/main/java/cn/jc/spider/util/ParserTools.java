package cn.jc.spider.util;

import org.jsoup.nodes.Element;

import cn.jc.spider.po.Parser;
import cn.jc.spider.po.Unvisitedurl;

public class ParserTools {

	public static String doselect(Element dd, Parser parser) {
		if ("html".equals(parser.getMethodtype())) {
			return dd.select(parser.getPattern()).html();
		} else if ("text".equals(parser.getMethodtype())) {
			return dd.select(parser.getPattern()).text();
		} else if ("attr".equals(parser.getMethodtype())) {
			return dd.select(parser.getPattern()).attr(parser.getAttrName());
		} else if ("next".equals(parser.getMethodtype())) {
			return dd.select(parser.getPattern()).get(0).nextSibling().toString();
		}
//		String name = s.select("div h2 a").html();
//		if (StringUtils.isBlank(name)) {
//			name = s.select("div h2").html();
//		}
		return dd.select(parser.getPattern()).outerHtml();
	}


	public static String fixUrl(Unvisitedurl url, String string) {
		if (string.startsWith("/")) {
			return "http://tj.58.com" + string;
		} else {
			return string;
		}
	}

}
