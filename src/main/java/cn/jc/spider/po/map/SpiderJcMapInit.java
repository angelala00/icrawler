package cn.jc.spider.po.map;

import org.apache.torque.TorqueException;

/**
 * This is a Torque Generated class that is used to load all database map 
 * information at once.  This is useful because Torque's default behaviour
 * is to do a "lazy" load of mapping information, e.g. loading it only
 * when it is needed.<p>
 *
 * @see org.apache.torque.map.DatabaseMap#initialize() DatabaseMap.initialize() 
 */
public class SpiderJcMapInit
{
    public static final void init()
        throws TorqueException
    {
        cn.jc.spider.po.CityDianpingPeer.getMapBuilder();
        cn.jc.spider.po.ParserPeer.getMapBuilder();
        cn.jc.spider.po.ParserCopyPeer.getMapBuilder();
        cn.jc.spider.po.ShangquanDianpingPeer.getMapBuilder();
        cn.jc.spider.po.SitePeer.getMapBuilder();
        cn.jc.spider.po.StorerPeer.getMapBuilder();
        cn.jc.spider.po.TaskPeer.getMapBuilder();
        cn.jc.spider.po.UnvisitedurlPeer.getMapBuilder();
        cn.jc.spider.po.VisitedurlPeer.getMapBuilder();
        cn.jc.spider.po.XiaohuaPeer.getMapBuilder();
    }
}
