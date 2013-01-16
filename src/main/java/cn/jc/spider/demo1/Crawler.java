package cn.jc.spider.demo1;

import java.io.IOException;
import java.util.Date;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;

import org.apache.commons.collections.CollectionUtils;
import org.apache.torque.TorqueException;
import org.apache.torque.util.Criteria;

import cn.jc.spider.InitTorque;
import cn.jc.spider.demo1.cache.Cache;
import cn.jc.spider.linkqueue.LinkQueueDB;
import cn.jc.spider.linkqueue.LinkQueueInterface;
import cn.jc.spider.po.App;
import cn.jc.spider.po.AppPeer;
import cn.jc.spider.po.Objectattr;
import cn.jc.spider.po.ObjectattrPeer;
import cn.jc.spider.po.Objectitem;
import cn.jc.spider.po.ObjectitemPeer;
import cn.jc.spider.po.Site;

public class Crawler {

	private LinkQueueInterface linkQueue;
//	private LinkQueueInterface linkQueue = new LinkQueueMem();
	private boolean running = false;
	private Site website = null;
	private Map<String, Map<String, String>> attrRegMap;

	public Crawler(Site site) {
		this.website = site;
		linkQueue = new LinkQueueDB(site.getWebsite());
		List<Objectattr> attrs = getAttrObject();
		Map<String, Map<String, String>> map = new HashMap<String, Map<String, String>>();
		for (Objectattr objectattr : attrs) {
			Map<String, String> map2 = new HashMap<String, String>();
			map2.put("reg", objectattr.getReg());
			map2.put("index", objectattr.getIndex()+"");
			map.put(objectattr.getAttrname(), map2);
		}
		setAttrRegMap(map);
		
	}

	public void initCrawlerWithSeeds(String[] seeds) {
		for (String url : seeds) {
			linkQueue.addUnVisitedUrl(url);
		}
	}

	/*
	 * http://www.mumayi.com/android-91988.html
	 * http://www.mumayi.com/android-91988.html#
	 * 两个URL页面内容相同的话如何处理
	 */
	public void crawling() {
		setRunning(true);
		LinkFilter filter_pa = new LinkFilter() {
			public boolean accept(String url) {
				if (url.matches(website.getMiddlepageurlreg())) {
					return true;
				} else {
//					System.out.println("丢弃页面：" + url);
					return false;
				}
			}
		};
		//没有访问过的队列不为空
		while (!linkQueue.unVisitedUrlIsEmpty() && running == true) {
//			System.out.println("--------------");
			String visitUrl = (String) linkQueue.unVisitedUrlDeQueue();
			if (visitUrl == null) {
				System.out.println(" visitUrl == null 什么个情況???");
				continue;
			}
			//判断一下，不需要的URL直接不匹配了
			if (visitUrl.matches(website.getTargetpageurlreg())) {
				try {
					FindData dataFinder;
//				long l1 = System.currentTimeMillis();
					dataFinder = new FindData(website.getWebsite(),visitUrl);
					long l2 = System.currentTimeMillis();
//				System.out.println("cost " + (l2 - l1) + " ms get content");
					Map<String, String> o = dataFinder.findObject(attrRegMap);
					long l3 = System.currentTimeMillis();
					saveObject(o);
					System.out.println("cost " + (l3 - l2) + " ms"+o + "::" + visitUrl);
				} catch (IOException e1) {
					System.out.println("什么个情况???超时的一部分数据？？？");
					e1.printStackTrace();
				}
			}
			//页面没打开
			//分析错误等都要记录到url里面
			
			linkQueue.addVisitedUrl(visitUrl);//上面方法抛异常了，这里还加吗�?
			Set<String> links;
			try {
				links = HtmlParserTool.extracLinks(visitUrl, filter_pa);//这里超时了怎么处理
				for (String link : links) {
					linkQueue.addUnVisitedUrl(link);
				}
			} catch (Throwable e) {
				//"https://www.google.com/accounts/ServiceLogin?service=androidmarket&passive=86400&continue=https://market.android.com/&followup=https://market.android.com/"
				//这个异常抓不到？？？？？？？
				System.out.println("eeeeeeeeexception"+visitUrl + filter_pa);
				//e.printStackTrace();
			}
		}
		System.out.println("!linkQueue.unVisitedUrlIsEmpty() && running == true     not   true");
	}
	
	public void crawlOnce(String visitUrl) {
		if (visitUrl == null) {
			System.out.println(" visitUrl == null 什么个情況???");
			return;
		}
		//判断一下，不需要的URL直接不匹配了
		if (visitUrl.matches(website.getTargetpageurlreg())) {
			try {
				FindData dataFinder;
				dataFinder = new FindData(website.getWebsite(),visitUrl);
				long l2 = System.currentTimeMillis();
				Map<String, String> o = dataFinder.findObject(attrRegMap);
				long l3 = System.currentTimeMillis();
				System.out.println("cost " + (l3 - l2) + " ms"+o + "::" + visitUrl);
			} catch (IOException e1) {
				System.out.println("什么个情况???超时的一部分数据？？？");
				e1.printStackTrace();
			}
		}
	}

	private void saveObject(Map<String, String> o) {
		Objectitem item = new Objectitem();
		item.setAppname(o.get("name"));
		item.setAppsize(o.get("size"));
		item.setAppdesc(o.get("desc"));
		item.setImgurl(o.get("imgurl"));
		item.setAppurl(o.get("appurl"));
		item.setWebsite(o.get("website"));
		item.setCreatetime(new Date());
		try {
			System.out.println(ObjectitemPeer.buildCriteria(item).toString());
			Criteria c = new Criteria();
			c.add(ObjectitemPeer.APPURL, item.getAppurl());
			List<Objectitem> os = ObjectitemPeer.doSelect(c);
			if (CollectionUtils.isNotEmpty(os)) {
				for (Objectitem oo : os) {
					oo.setAppname(item.getAppname());
					oo.setAppsize(item.getAppsize());
					oo.setAppdesc(item.getAppdesc());
					oo.setImgurl(item.getImgurl());
					oo.save();
				}
			} else {
				item.save();
			}
		} catch (Exception e) {
			e.printStackTrace();
		}
	}
	private void saveObject2(Map<String, String> o) {
		App item = new App();
		item.setAppname(o.get("name"));
		item.setSize(o.get("size"));
		item.setDescription(o.get("desc"));
		item.setImgUrl(o.get("imgurl"));
		item.setViewUrl(o.get("appurl"));
		item.setProvider(o.get("website"));
		item.setUpdatetime(new Date());
		try {
			System.out.println(AppPeer.buildCriteria(item).toString());
			Criteria c = new Criteria();
			c.add(AppPeer.APPNAME, item.getAppname());
			c.add(AppPeer.PROVIDER, item.getProvider());
			List<App> os = AppPeer.doSelect(c);
			if (CollectionUtils.isNotEmpty(os)) {
				for (App oo : os) {
					oo.setSize(item.getSize());
					oo.setDescription(item.getDescription());
					oo.setImgUrl(item.getImgUrl());
					oo.setViewUrl(item.getViewUrl());
					oo.save();
				}
			} else {
				item.save();
			}
		} catch (Exception e) {
			e.printStackTrace();
		}
	}

	public static void main(String[] args) {
//		String reg = "http://www.mumayi.com/(?!(wallpaper|plus|tag)).*";
//		System.out.println("http://www.mumayi.com/wallpaper/app/".matches(reg));
//		System.out.println("http://www.mumayi.com/android/app/".matches(reg));
//		System.out.println("http://www.mumayi.com/plus/today.php?date=2012-05-24&typeid=6".matches(reg));
//		System.out.println("http://www.mumayi.com/tag/18/xiezaigongju_18535_1.html".matches(reg));
//		System.out.println("http://www.mumayi.com/plus-view.php?aid=30893".matches(reg));
		
//		System.out.println(Pattern.compile("http://www.mumayi.com/android-\\d*.html").matcher("http://www.mumayi.com/android-special-103596.html").matches());
		InitTorque.init();
		Site site = Cache.siteMap.get("mumayi");
		if (site != null) {
			Crawler mc = new Crawler(site);
			mc.initCrawlerWithSeeds(new String[] {site.getWebsitesuperurl(), "http://www.mumayi.com/android-38442.html"});
			mc.crawling();
//			mc.crawlOnce("http://www.mumayi.com/android-24613.html");
		}
	}

	private List<Objectattr> getAttrObject() {
		try {
			Criteria c = new Criteria()	;
			c.add(ObjectattrPeer.WEBSITE, website.getWebsite());
			return ObjectattrPeer.doSelect(c);
		} catch (TorqueException e) {
			e.printStackTrace();
		}
		return null;
	}

	public LinkQueueInterface getLinkQueue() {
		return linkQueue;
	}

	public void setLinkQueue(LinkQueueInterface linkQueue) {
		this.linkQueue = linkQueue;
	}

	public boolean isRunning() {
		return running;
	}

	public void setRunning(boolean running) {
		this.running = running;
	}

	public Site getWebsite() {
		return website;
	}

	public void setWebsite(Site website) {
		this.website = website;
	}

	public Map<String, Map<String, String>> getAttrRegMap() {
		return attrRegMap;
	}

	public void setAttrRegMap(Map<String, Map<String, String>> attrRegMap) {
		this.attrRegMap = attrRegMap;
	}
	

}
