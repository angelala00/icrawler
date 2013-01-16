package cn.jc.spider.neww;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.apache.commons.collections.CollectionUtils;
import org.apache.commons.collections.MapUtils;
import org.apache.commons.lang.StringUtils;
import org.apache.torque.TorqueException;
import org.apache.torque.util.BasePeer;
import org.apache.torque.util.Criteria;
import org.jsoup.Jsoup;
import org.jsoup.nodes.Document;
import org.jsoup.nodes.Element;
import org.jsoup.select.Elements;

import cn.jc.spider.po.Parser;
import cn.jc.spider.po.Task;
import cn.jc.spider.po.Unvisitedurl;
import cn.jc.spider.po.UnvisitedurlPeer;
import cn.jc.spider.util.ParserTools;

/**
 * @author JiangChi
 *
 */
public class ParserImpl_jsoup implements ParserI {
	private List<Parser> ps;
	private Map<String, Parser> psmap = new HashMap<String, Parser>();
	private Task task;

	public ParserImpl_jsoup(Task task, List<Parser> ps) {
		if (task == null) {
			System.out.println("task is null");
		}
		if (CollectionUtils.isEmpty(ps)) {
			System.out.println("ps is null");
		}
		this.ps = ps;
		for (Parser p : ps) {
			psmap.put(p.getAttr(), p);
		}
		this.task = task;
	}

	@Override
	public Map<String, Object> parseToMap(String content) {
		List<Parser> pss = new ArrayList<Parser>();
		for (Parser p : ps) {
			if (p.getPid() == 0) {
				pss.add(p);
			}
		}
		Map<String, Object> map = parse(content, pss);
		return map;
	}

	private Map<String, Object> parse(String content,List<Parser> ps) {
		Document s = Jsoup.parse(content);
		Map<String, Object> map = new HashMap<String, Object>();
		if (CollectionUtils.isNotEmpty(ps)) {
			for (Parser parser : ps) {
				//如果是个list<Object>
				if ("list".equals(parser.getNodatype())) {
					Elements ds = s.select(parser.getPattern());
					List<Map<String, Object>> list = new ArrayList<Map<String, Object>>();
					if (ds != null && ds.size() > 0) {
						for (Element dd : ds) {
							///查询到子paserList 递归调用
							list.add(parse(dd.toString(),getsubparserlist(parser.getId())));
						}
					}
					map.put(parser.getAttr(), list);
				} else {//如果是个Object				
					map.put(parser.getAttr(), ParserTools.doselect(s, parser));
				}
			}
		}
		return map;
	}
	private List<Parser> getsubparserlist(int id) {
		List<Parser> result_ps = new ArrayList<Parser>();
		for (Parser parser : ps) {
			if (parser.getPid() == id) {
				result_ps.add(parser);
			}
		}
		return result_ps;
	}

	@Override
	public List<String> parsePages(String content) {
		Document s = Jsoup.parse(content);
		String findpagepattern = psmap.get("findpage").getPattern();
		if (StringUtils.isNotBlank(findpagepattern)) {
			Elements ds = s.select(findpagepattern);
			List<String> list = new ArrayList<String>();
			if (ds != null && ds.size() > 0) {
				for (Element dd : ds) {
					//if()判断前10页，10页后就不要了（对于58同城是这样的）这里弄个正则，写到数据库里？
					list.add(dd.attr("href"));
				}
				return list;
			} else {
				return null;
			}
		} else {
			return null;
		}
	}
	@Override
	public void runsaveinfo(Unvisitedurl url, Map<String, Object> jiexicontent) {
		if (MapUtils.isNotEmpty(jiexicontent)) {
			if (jiexicontent.size() == 1) {
				List<Map<String, Object>> list = (List<Map<String, Object>>) jiexicontent.get("list");
				for (Map<String, Object> m : list) {
					String ssa = "";
					String ssb = "";
					String prefix = "";
					for (Parser s : ps) {//原来是ss1
						if (ssa.length() != 0 && ssb.length() != 0) {
							prefix = ",";
						}
						ssa += prefix + "`" + s.getAttr() + "`";
						ssb += prefix + "'" + m.get(s.getAttr()) + "'";
					}
					if (task.getIdNext() > 0) {
						
						if (psmap.get("fuzhubiaoshiid") != null) {
							//这里只是特定的地方用到
							Criteria cc = new Criteria();
							cc.add(UnvisitedurlPeer.FUZHUBIAOSHIID, m.get("fuzhubiaoshiid"));
							List<Unvisitedurl> uns = null;
							try {
								uns = UnvisitedurlPeer.doSelect(cc);
							} catch (TorqueException e1) {
							}
							if (CollectionUtils.isNotEmpty(uns)) {
//						System.out.println("公司重复略过 公司名："+m.get("fuzhubiaoshiid")+" url:"+url.getUrl());
								continue;
							}
						}
						
						String ss1 = "insert into unvisitedurl (`id_task`,`url`,`fuzhubiaoshiid`) values(" + task.getIdNext() + ",'" + ParserTools.fixUrl(url, (String)m.get("href")) + "','"+m.get("fuzhubiaoshiid")+"')";
						try {
							Criteria c = new Criteria();
							c.add(UnvisitedurlPeer.URL, ParserTools.fixUrl(url, (String)m.get("href")));
							List<Unvisitedurl> us = UnvisitedurlPeer.doSelect(c);
							if (CollectionUtils.isEmpty(us)) {
								BasePeer.executeStatement(ss1);
							} else {
								
							}
						} catch (TorqueException e) {
							e.printStackTrace();
							System.out.println("插入数据库异常 sql:" + ss1);
						}
					} else {
						String ss = "insert into "+task.getName()+" (" + ssa + ") values(" + ssb + ")";
						try {
							BasePeer.executeQuery(ss);
						} catch (TorqueException e) {
							e.printStackTrace();
							System.out.println("插入数据库异常 sql:" + ss);
						}
					}
				}
			}
		}
	}
	
}
