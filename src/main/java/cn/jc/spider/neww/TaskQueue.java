package cn.jc.spider.neww;

import java.util.List;

import org.apache.commons.collections.CollectionUtils;
import org.apache.torque.TorqueException;
import org.apache.torque.util.Criteria;

import cn.jc.spider.po.Parser;
import cn.jc.spider.po.ParserPeer;
import cn.jc.spider.po.Task;
import cn.jc.spider.po.TaskPeer;

public class TaskQueue {

	public static Task getTask(int timetime) {
		Criteria c = new Criteria();
		c.add(TaskPeer.TIMETIME, timetime, Criteria.NOT_EQUAL);
		List<Task> ts = null;
		try {
			ts = TaskPeer.doSelect(c);
		} catch (TorqueException e) {
			e.printStackTrace();
			System.out.println("查询Task异常 sql:" + c.toString());
		}
		if (CollectionUtils.isEmpty(ts)) {
			return null;
		}
		final Task task = ts.get(0);
		List<Parser> ps = null;
		c = new Criteria();
		c.add(ParserPeer.ID_TASK, task.getId());
		try {
			ps = ParserPeer.doSelect(c);
		} catch (TorqueException e) {
			System.out.println("查询Parser异常 sql:" + c.toString());
		}
		if (CollectionUtils.isEmpty(ps)) {
			return null;
		}
		ParserI parser = new ParserImpl_jsoup(task,ps);
		task.setJiexiqi(parser);
//		List<Storer> ss = null;
//		c = new Criteria();
//		c.add(StorerPeer.ID_TASK, task.getId());
//		try {
//			ss = StorerPeer.doSelect(c);
//		} catch (TorqueException e) {
//			System.out.println("查询storer异常 sql:" + c.toString());
//		}
//		if (CollectionUtils.isEmpty(ss)) {
//			return null;
//		}
//		final List<Storer> ss1 = ss;
		return task;
	}

}
