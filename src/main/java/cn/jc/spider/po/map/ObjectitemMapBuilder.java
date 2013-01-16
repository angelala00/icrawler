package cn.jc.spider.po.map;

import java.util.Date;
import java.math.BigDecimal;

import org.apache.torque.Torque;
import org.apache.torque.TorqueException;
import org.apache.torque.adapter.DB;
import org.apache.torque.map.MapBuilder;
import org.apache.torque.map.DatabaseMap;
import org.apache.torque.map.TableMap;
import org.apache.torque.map.ColumnMap;
import org.apache.torque.map.InheritanceMap;

/**
  */
public class ObjectitemMapBuilder implements MapBuilder
{
    /**
     * The name of this class
     */
    public static final String CLASS_NAME =
        "cn.jc.spider.po.map.ObjectitemMapBuilder";

    /**
     * The database map.
     */
    private DatabaseMap dbMap = null;

    /**
     * Tells us if this DatabaseMapBuilder is built so that we
     * don't have to re-build it every time.
     *
     * @return true if this DatabaseMapBuilder is built
     */
    public boolean isBuilt()
    {
        return (dbMap != null);
    }

    /**
     * Gets the databasemap this map builder built.
     *
     * @return the databasemap
     */
    public DatabaseMap getDatabaseMap()
    {
        return this.dbMap;
    }

    /**
     * The doBuild() method builds the DatabaseMap
     *
     * @throws TorqueException
     */
    public synchronized void doBuild() throws TorqueException
    {
        if ( isBuilt() ) {
            return;
        }
        dbMap = Torque.getDatabaseMap("spider_jc");

        dbMap.addTable("objectitem");
        TableMap tMap = dbMap.getTable("objectitem");
        tMap.setJavaName("Objectitem");
        tMap.setOMClass( cn.jc.spider.po.Objectitem.class );
        tMap.setPeerClass( cn.jc.spider.po.ObjectitemPeer.class );
        tMap.setPrimaryKeyMethod(TableMap.NATIVE);
        DB dbAdapter = Torque.getDB("spider_jc");
        if (dbAdapter.getIDMethodType().equals(DB.SEQUENCE))
        {
            tMap.setPrimaryKeyMethodInfo("objectitem_SEQ");
        }
        else if (dbAdapter.getIDMethodType().equals(DB.AUTO_INCREMENT))
        {
            tMap.setPrimaryKeyMethodInfo("objectitem");
        }

        ColumnMap cMap = null;


  // ------------- Column: id --------------------
        cMap = new ColumnMap( "id", tMap);
        cMap.setType( new Integer(0) );
        cMap.setTorqueType( "INTEGER" );
        cMap.setUsePrimitive(true);
        cMap.setPrimaryKey(true);
        cMap.setNotNull(true);
        cMap.setJavaName( "Id" );
        cMap.setAutoIncrement(true);
        cMap.setProtected(false);
        cMap.setInheritance("false");
        cMap.setPosition(1);
        tMap.addColumn(cMap);
  // ------------- Column: website --------------------
        cMap = new ColumnMap( "website", tMap);
        cMap.setType( "" );
        cMap.setTorqueType( "VARCHAR" );
        cMap.setUsePrimitive(true);
        cMap.setPrimaryKey(false);
        cMap.setNotNull(false);
        cMap.setJavaName( "Website" );
        cMap.setAutoIncrement(false);
        cMap.setProtected(false);
        cMap.setInheritance("false");
        cMap.setSize( 50 );
        cMap.setPosition(2);
        tMap.addColumn(cMap);
  // ------------- Column: appname --------------------
        cMap = new ColumnMap( "appname", tMap);
        cMap.setType( "" );
        cMap.setTorqueType( "VARCHAR" );
        cMap.setUsePrimitive(true);
        cMap.setPrimaryKey(false);
        cMap.setNotNull(false);
        cMap.setJavaName( "Appname" );
        cMap.setAutoIncrement(false);
        cMap.setProtected(false);
        cMap.setInheritance("false");
        cMap.setSize( 50 );
        cMap.setPosition(3);
        tMap.addColumn(cMap);
  // ------------- Column: appsize --------------------
        cMap = new ColumnMap( "appsize", tMap);
        cMap.setType( "" );
        cMap.setTorqueType( "VARCHAR" );
        cMap.setUsePrimitive(true);
        cMap.setPrimaryKey(false);
        cMap.setNotNull(false);
        cMap.setJavaName( "Appsize" );
        cMap.setAutoIncrement(false);
        cMap.setProtected(false);
        cMap.setInheritance("false");
        cMap.setSize( 10 );
        cMap.setPosition(4);
        tMap.addColumn(cMap);
  // ------------- Column: appurl --------------------
        cMap = new ColumnMap( "appurl", tMap);
        cMap.setType( "" );
        cMap.setTorqueType( "VARCHAR" );
        cMap.setUsePrimitive(true);
        cMap.setPrimaryKey(false);
        cMap.setNotNull(false);
        cMap.setJavaName( "Appurl" );
        cMap.setAutoIncrement(false);
        cMap.setProtected(false);
        cMap.setInheritance("false");
        cMap.setSize( 100 );
        cMap.setPosition(5);
        tMap.addColumn(cMap);
  // ------------- Column: imgurl --------------------
        cMap = new ColumnMap( "imgurl", tMap);
        cMap.setType( "" );
        cMap.setTorqueType( "VARCHAR" );
        cMap.setUsePrimitive(true);
        cMap.setPrimaryKey(false);
        cMap.setNotNull(false);
        cMap.setJavaName( "Imgurl" );
        cMap.setAutoIncrement(false);
        cMap.setProtected(false);
        cMap.setInheritance("false");
        cMap.setSize( 100 );
        cMap.setPosition(6);
        tMap.addColumn(cMap);
  // ------------- Column: appdesc --------------------
        cMap = new ColumnMap( "appdesc", tMap);
        cMap.setType( "" );
        cMap.setTorqueType( "VARCHAR" );
        cMap.setUsePrimitive(true);
        cMap.setPrimaryKey(false);
        cMap.setNotNull(false);
        cMap.setJavaName( "Appdesc" );
        cMap.setAutoIncrement(false);
        cMap.setProtected(false);
        cMap.setInheritance("false");
        cMap.setSize( 500 );
        cMap.setPosition(7);
        tMap.addColumn(cMap);
  // ------------- Column: createtime --------------------
        cMap = new ColumnMap( "createtime", tMap);
        cMap.setType( new Date() );
        cMap.setTorqueType( "TIMESTAMP" );
        cMap.setUsePrimitive(true);
        cMap.setPrimaryKey(false);
        cMap.setNotNull(false);
        cMap.setJavaName( "Createtime" );
        cMap.setAutoIncrement(false);
        cMap.setProtected(false);
        cMap.setInheritance("false");
        cMap.setPosition(8);
        tMap.addColumn(cMap);
        tMap.setUseInheritance(false);
    }
}
