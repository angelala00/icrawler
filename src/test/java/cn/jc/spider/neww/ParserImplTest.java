package cn.jc.spider.neww;

import java.util.List;
import java.util.Map;

import junit.framework.TestCase;
import net.sf.json.JSONObject;

import org.apache.commons.collections.CollectionUtils;
import org.apache.torque.TorqueException;
import org.apache.torque.linkage.SpiderJcMapInit;
import org.apache.torque.util.Criteria;

import cn.jc.spider.po.Parser;
import cn.jc.spider.po.ParserPeer;
import cn.jc.spider.po.Task;
import cn.jc.spider.po.TaskPeer;
import cn.jc.spider.util.HttpTools;

public class ParserImplTest extends TestCase {

	public void testParse() {

		SpiderJcMapInit.init_my();
		int taskid = 4;
		
		List<Task> ts = null;
		Criteria c = new Criteria();
		try {
			c.add(TaskPeer.ID, taskid);
			ts = TaskPeer.doSelect(c);
		} catch (TorqueException e) {
			e.printStackTrace();
			System.out.println("查询Task异常 sql:" + c.toString());
		}
		Task task = null;
		if (!CollectionUtils.isEmpty(ts)) {
			task = ts.get(0);
		}
		

		Criteria cc = new Criteria();
		List<Parser> ps = null;
		try {
			cc.add(ParserPeer.ID_TASK, taskid);
			ps = ParserPeer.doSelect(cc);
		} catch (TorqueException e) {
			e.printStackTrace();
			System.out.println("查询Task异常 sql:" + cc.toString());
		}
		
		ParserI pi = new ParserImpl_jsoup(task, ps);
		String content = HttpTools.getContentFromUrlByGet("http://bj.58.com/renli/12366745949959x.shtml", null, null, null);
		Map<String, Object> o = pi.parseToMap(content);
		System.out.println(o);
//		fail("Not yet implemented");
	}

	public void testParseList() {
		fail("Not yet implemented");
	}

	public static void main(String args[]){
		SpiderJcMapInit.init_my();
//		getonetime(5,"http://fayuzhinan.duapp.com/fayu-2.html","UTF-8");
		getonetime(8,"http://www.kl688.com/newjokes/index_3867.htm","GBK");
	}

	private static void getonetime(int taskid, String url, String encode) {
		List<Task> ts = null;
		Criteria c = new Criteria();
		try {
			c.add(TaskPeer.ID, taskid);
			ts = TaskPeer.doSelect(c);
		} catch (TorqueException e) {
			e.printStackTrace();
			System.out.println("查询Task异常 sql:" + c.toString());
		}
		Task task = null;
		if (!CollectionUtils.isEmpty(ts)) {
			task = ts.get(0);
		}
		
		Criteria cc = new Criteria();
		List<Parser> ps = null;
		try {
			cc.add(ParserPeer.ID_TASK, task.getId());
			ps = ParserPeer.doSelect(cc);
		} catch (TorqueException e) {
			e.printStackTrace();
			System.out.println("查询Task异常 sql:" + cc.toString());
		}
		
		
		ParserI parser = new ParserImpl_jsoup(task, ps);
		String content = HttpTools.getContentFromUrlByGet(url, null, null, encode);
		
//		System.out.println(content);
		
		Map<String, Object> o = parser.parseToMap(content);
		
		List<Map<String,Object>> ml = (List<Map<String, Object>>) o.get("xiaohualist");
		for (Map<String,Object> m : ml) {
			System.out.println(m);
		}
		
		JSONObject json = JSONObject.fromObject(o);
//		System.out.println(json.toString());
	
	}
}
