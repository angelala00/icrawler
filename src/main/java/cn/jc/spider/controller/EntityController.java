package cn.jc.spider.controller;


import java.io.IOException;
import java.util.Collection;

import javax.servlet.http.Cookie;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import org.apache.log4j.Logger;
import org.apache.torque.TorqueException;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;

import cn.jc.spider.Pool;
import cn.jc.spider.demo1.Crawler;
import cn.jc.spider.demo1.cache.Cache;
import cn.jc.spider.linkqueue.LinkQueueInterface;
import cn.jc.spider.po.Site;


/**
 * Handles requests for the application home page.
 */
@Controller
public class EntityController {

	private static final Logger logger = Logger.getLogger(EntityController.class); 

	@RequestMapping(value="/viewsites.do", method=RequestMethod.GET)
	public String getChannelList(HttpServletRequest request,HttpServletResponse response) {
		Collection<Crawler> crawlers = Pool.getCrawlers();
		request.setAttribute("crawlers", crawlers);
		return "spiders";
	}
	@RequestMapping(value="/view.do", method=RequestMethod.GET)
	public String viewstatus(HttpServletRequest request,HttpServletResponse response) {
		String website = request.getParameter("site")	;
		website = "mumayi";
		Site site = Cache.siteMap.get(website);
		if (site != null) {
			Crawler mc = Pool.getCrawler(site.getWebsite());
			if (mc != null) {
				LinkQueueInterface lq = mc.getLinkQueue();
				request.setAttribute("num", lq.getVisitedUrlNum());
			} else {
				System.out.println("什么个情况？？？");
			}
		} else {
			System.out.println("错误的site");
		}
		return "spiders";
	}
	@RequestMapping(value="/restart.do", method=RequestMethod.GET)
	public String restart(HttpServletRequest request,HttpServletResponse response) {
//		if (MyCrawler.running != true && !LinkQueue.unVisitedUrlIsEmpty()) {
//			MyCrawler.running =true;
//			MyCrawler.crawling();
//			request.setAttribute("num", LinkQueue.getVisitedUrlNum());
//			System.out.println("restarted");
//		} else {
//			System.out.println("no action");
//		}
		return "spiders";
	}
	@RequestMapping(value="/start.do", method=RequestMethod.GET)
	public String start(HttpServletRequest request,HttpServletResponse response) {
		String website = request.getParameter("site")	;
		website = "mumayi";
		Site site = Cache.siteMap.get(website);
		if (site != null) {
			Crawler mc = Pool.getCrawler(site.getWebsite());
			if (mc != null) {
				if (!mc.isRunning()) {
					LinkQueueInterface lq = mc.getLinkQueue();
					if (!lq.unVisitedUrlIsEmpty()) {
						mc.crawling();
						System.out.println(site.getWebsite()+"...continue");
					} else {
						//重新启动的时候，要把两个url表给清空吧 TODO
						mc.initCrawlerWithSeeds(new String[] { site.getWebsitesuperurl() });
						System.out.println("new start");
					}
				}
			} else {
				System.out.println("什么个情况？？？");
			}
		} else {
			System.out.println("错误的site");
		}
		return "spiders";
	}
	@RequestMapping(value="/stop.do", method=RequestMethod.GET)
	public String stop(HttpServletRequest request,HttpServletResponse response) {
		String website = request.getParameter("site")	;
		website = "mumayi";
		Site site = Cache.siteMap.get(website);
		if (site != null) {
			Crawler mc = Pool.getCrawler(site.getWebsite());
			if (mc != null) {
				if (mc.isRunning()) {
					mc.setRunning(false);
				}
			} else {
				System.out.println("什么个情况？？？");
			}
		} else {
			System.out.println("错误的site");
		}
		return "spiders";
	}
	private String getCookie(HttpServletRequest request, String string) {
		Cookie[] ss = request.getCookies();
		if(ss!=null){
			for (Cookie s : ss) {
				if (string.equals(s.getName())) {
					return s.getValue();
				}
			}
		}
		return "";
	}
	/**
	 * 获得系统时间
	 * @param request
	 * @param response
	 * @return
	 * @throws TorqueException
	 * @author JiangChi
	 */
	@RequestMapping(value="/getsystime.do", method=RequestMethod.GET)
	public String getsystime(HttpServletRequest request,HttpServletResponse response) throws TorqueException{
		try {
			response.setContentType("text/html;charset=UTF-8");
			response.getWriter().write(""+System.currentTimeMillis());
			response.getWriter().flush();
		} catch (IOException e) {
			e.printStackTrace();
		}
		return null;
	}
}

