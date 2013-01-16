package cn.jc.spider.demo1.cache;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.apache.torque.TorqueException;
import org.apache.torque.util.Criteria;

import cn.jc.spider.po.Site;
import cn.jc.spider.po.SitePeer;

public class Cache {

	public static Map<String, Site> siteMap = new HashMap<String, Site>();
	static {
		try {
			List<Site> sites = SitePeer.doSelect(new Criteria());
			for (Site site : sites) {
				siteMap.put(site.getWebsite(), site);
			}
		} catch (TorqueException e) {
			e.printStackTrace();
		}
	}

}
