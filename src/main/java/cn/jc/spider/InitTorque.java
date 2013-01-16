package cn.jc.spider;

import org.apache.torque.Torque;
import org.apache.torque.TorqueException;

public class InitTorque {
	public InitTorque(){
		init();
	}
	public static void init() {
		try {
			Torque.init("spiderTorque.properties");
			System.out.println("初始化成功");
		} catch (TorqueException e) {
			System.out.println("初始化失败");
			e.printStackTrace();
		}
	}

}
