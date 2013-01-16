package cn.jc.spider.linkqueue;

import java.util.List;

import org.apache.commons.collections.CollectionUtils;
import org.apache.commons.lang.StringUtils;
import org.apache.torque.TorqueException;
import org.apache.torque.util.Criteria;

import cn.jc.spider.po.Unvisitedurl;
import cn.jc.spider.po.UnvisitedurlPeer;
import cn.jc.spider.po.Visitedurl;
import cn.jc.spider.po.VisitedurlPeer;

import com.workingdogs.village.Record;


public class LinkQueueDB implements LinkQueueInterface {

	private String website;
	public LinkQueueDB() {
		super();
	}

	public LinkQueueDB(String website) {
		this.website = website;
	}

	@Override
	public void addVisitedUrl(String url) {
		try {
			Visitedurl urlO = new Visitedurl();
			urlO.setUrl(url);
			urlO.setWebsite(website);
			urlO.save();
		} catch (Exception e) {
			System.out.println("exception addVisitedUrl : " + url);
			e.printStackTrace();
		}
	}

	@Override
	public Object unVisitedUrlDeQueue() {
		try {
			Criteria c1 = new Criteria();
			c1.add(UnvisitedurlPeer.WEBSITE, website);
			c1.setLimit(1);
			c1.addAscendingOrderByColumn(UnvisitedurlPeer.ID);
			List<Unvisitedurl> uvurls = UnvisitedurlPeer.doSelect(c1);
			if (CollectionUtils.isNotEmpty(uvurls)) {
				Criteria c = new Criteria();
				c.add(UnvisitedurlPeer.ID, uvurls.get(0).getId());
				UnvisitedurlPeer.doDelete(c );
				return uvurls.get(0).getUrl();
			}
		} catch (TorqueException e) {
			e.printStackTrace();
		}
		return null;
	}

	@Override
	public void addUnVisitedUrl(String url) {
		if (StringUtils.isNotBlank(url)) {
			url = url.split("#")[0];
			try {
				Criteria c1 = new Criteria();
				c1.add(UnvisitedurlPeer.WEBSITE, website);
				c1.add(UnvisitedurlPeer.URL, url);
				List<Unvisitedurl> uvurls = UnvisitedurlPeer.doSelect(c1);
				Criteria c2 = new Criteria();
				c2.add(VisitedurlPeer.WEBSITE, website);
				c2.add(VisitedurlPeer.URL, url);
				List<Visitedurl> vurls = VisitedurlPeer.doSelect(c2);
				if (CollectionUtils.isEmpty(uvurls)	&& CollectionUtils.isEmpty(vurls)) {
//					System.out.println("addurl : " + url);
					Unvisitedurl urlO = new Unvisitedurl();
					urlO.setUrl(url);
					urlO.setWebsite(website);
					urlO.save();
				}
			} catch (Exception e) {
				System.out.println("exception addUnVisitedUrl : " + url);
				e.printStackTrace();
			}
		}
	}

	@Override
	public int getUnVisitedUrlNum() {
		StringBuffer sb = new StringBuffer("SELECT COUNT(*) c FROM unvisitedurl where website = '" + website + "'");
		try {
			List<Record> list = UnvisitedurlPeer.executeQuery(sb.toString());
			int num = list.get(0).getValue("c").asInt();
			return num;
		} catch (Exception e) {
			e.printStackTrace();
		}
		return -1;
	}
	@Override
	public int getVisitedUrlNum() {
		StringBuffer sb = new StringBuffer("SELECT COUNT(*) c FROM visitedurl where website = '" + website + "'");
		try {
			List<Record> list = VisitedurlPeer.executeQuery(sb.toString());
			int num = list.get(0).getValue("c").asInt();
			return num;
		} catch (Exception e) {
			e.printStackTrace();
		}
		return -1;
	}

	@Override
	public boolean unVisitedUrlIsEmpty() {
		StringBuffer sb = new StringBuffer("SELECT COUNT(*) c FROM unvisitedurl where website = '" + website + "'");
		try {
			List<Record> list = UnvisitedurlPeer.executeQuery(sb.toString());
			int num = list.get(0).getValue("c").asInt();
			return num <= 0;
		} catch (Exception e) {
			e.printStackTrace();
		}
		return true;
	}

	public String getWebsite() {
		return website;
	}

	public void setWebsite(String website) {
		this.website = website;
	}
	
	public static void main(String args[]){
		String url = "http://www.mumayi.com/android-70712.html#headshowlogo";
		url= url.split("#")[0];
		System.out.println(url);
	}

}
