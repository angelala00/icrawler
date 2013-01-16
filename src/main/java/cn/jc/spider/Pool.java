package cn.jc.spider;

import java.util.Collection;
import java.util.HashMap;
import java.util.Map;

import cn.jc.spider.demo1.Crawler;
import cn.jc.spider.demo1.cache.Cache;
import cn.jc.spider.po.Site;

public class Pool {

	public static Map<String, Crawler> spiderMap = new HashMap<String, Crawler>();
	static {
		Crawler value = null;
		spiderMap.put("", value);
	}

	public static Crawler getCrawler(String website) {
		if (!spiderMap.containsKey(website)) {
			Site site = Cache.siteMap.get(website);
			Crawler mc = new Crawler(site);
			spiderMap.put(website, mc);
		}
		return spiderMap.get(website);
	}
	public static Collection<Crawler> getCrawlers() {
		for (Site site : Cache.siteMap.values()) {
			if (!spiderMap.containsKey(site.getWebsite())) {
				Crawler mc = new Crawler(site);
				spiderMap.put(site.getWebsite(), mc);
			}
		}
		return spiderMap.values();
	}

}
