package cn.jc.spider.controller;


import java.io.IOException;
import java.sql.Time;
import java.util.Collection;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import javax.servlet.http.Cookie;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import javax.servlet.http.HttpSession;

import net.sf.json.JSONArray;

import org.apache.commons.collections.CollectionUtils;
import org.apache.log4j.Logger;
import org.apache.torque.TorqueException;
import org.apache.torque.util.Criteria;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.ResponseBody;

import com.google.gson.ExclusionStrategy;
import com.google.gson.FieldAttributes;
import com.google.gson.GsonBuilder;
import com.google.gson.internal.bind.TimeTypeAdapter;

import cn.jc.spider.Pool;
import cn.jc.spider.demo1.Crawler;
import cn.jc.spider.demo1.cache.Cache;
import cn.jc.spider.linkqueue.LinkQueueInterface;
import cn.jc.spider.po.Site;
import cn.jc.spider.po.Task;
import cn.jc.spider.po.TaskPeer;


/**
 * Handles requests for the application home page.
 */
@Controller
public class EntityController_new {

	private static final Logger logger = Logger.getLogger(EntityController_new.class); 

	@RequestMapping(value="/get_tasks.do")
	public String getChannelList(HttpServletRequest request,HttpServletResponse response) throws TorqueException {
		Criteria c = new Criteria();
		List<Task> ts = TaskPeer.doSelect(c);
//		System.out.println(toJson(ts, ""));//{"total":"1","rows":[{"id":"23210","firstname":"1212","lastname":"1212","phone":"1212","email":"1212@12.com"}]}
		writejson(toJson(warpJson(ts), ""),response);
		return null;
	}
	private Object warpJson(List<Task> ts) {
		Map<String, Object> map = new HashMap<String, Object>();
		map.put("total", CollectionUtils.isNotEmpty(ts) ? ts.size() : 0);
		map.put("rows", ts);
		return map;
	}
	/**
	 * 直接返回JSON对象，这里没成功，有问题
	 * @param session
	 * @return
	 * @throws TorqueException
	 */
	@RequestMapping(value="/get_tasks1.do")
	@ResponseBody
	public Object getChannelList1(HttpSession session) throws TorqueException {
		Criteria c = new Criteria();
		List<Task> ts = TaskPeer.doSelect(c);
		System.out.println("===========");
		return ts;
	}
	@RequestMapping(value="/viewtask.do", method=RequestMethod.GET)
	public String viewstatus(HttpServletRequest request,HttpServletResponse response) {
		return "spiders";
	}
	@RequestMapping(value="/restarttask.do", method=RequestMethod.GET)
	public String restart(HttpServletRequest request,HttpServletResponse response) {
		return "spiders";
	}
	@RequestMapping(value="/starttask.do", method=RequestMethod.GET)
	public String start(HttpServletRequest request,HttpServletResponse response) {
		return "spiders";
	}
	@RequestMapping(value="/stoptask.do", method=RequestMethod.GET)
	public String stop(HttpServletRequest request,HttpServletResponse response) {
		return "spiders";
	}
	protected void writejson(String result, HttpServletResponse response) {
		try {
			response.setContentType("text/html;charset=UTF-8");
			response.getWriter().write(result);
		} catch (IOException e) {
			e.printStackTrace();
		}
	}
	public static String toJson(Object s, final String desc) {
		GsonBuilder v = new GsonBuilder();
		v.setDateFormat("yyyy-MM-dd HH:mm:ss");
		v.registerTypeAdapter(Time.class, TimeTypeAdapter.FACTORY);
		v.setExclusionStrategies(new ExclusionStrategy(){
			@Override
			public boolean shouldSkipClass(Class<?> arg0) {
				return false;
			}
			@Override
			public boolean shouldSkipField(FieldAttributes attr) {
				if (desc.contains("|" + attr.getName() + "|")) {
					return true;
				}
				return false;
			}
		});
		String ss = v.create().toJson(s);
		return ss;
	}
}

