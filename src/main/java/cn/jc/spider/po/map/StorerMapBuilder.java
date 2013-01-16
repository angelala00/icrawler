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
public class StorerMapBuilder implements MapBuilder
{
    /**
     * The name of this class
     */
    public static final String CLASS_NAME =
        "cn.jc.spider.po.map.StorerMapBuilder";

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

        dbMap.addTable("storer");
        TableMap tMap = dbMap.getTable("storer");
        tMap.setJavaName("Storer");
        tMap.setOMClass( cn.jc.spider.po.Storer.class );
        tMap.setPeerClass( cn.jc.spider.po.StorerPeer.class );
        tMap.setPrimaryKeyMethod(TableMap.NATIVE);
        DB dbAdapter = Torque.getDB("spider_jc");
        if (dbAdapter.getIDMethodType().equals(DB.SEQUENCE))
        {
            tMap.setPrimaryKeyMethodInfo("storer_SEQ");
        }
        else if (dbAdapter.getIDMethodType().equals(DB.AUTO_INCREMENT))
        {
            tMap.setPrimaryKeyMethodInfo("storer");
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
  // ------------- Column: id_task --------------------
        cMap = new ColumnMap( "id_task", tMap);
        cMap.setType( new Integer(0) );
        cMap.setTorqueType( "INTEGER" );
        cMap.setUsePrimitive(true);
        cMap.setPrimaryKey(false);
        cMap.setNotNull(false);
        cMap.setJavaName( "IdTask" );
        cMap.setAutoIncrement(false);
        cMap.setProtected(false);
        cMap.setInheritance("false");
        cMap.setPosition(2);
        tMap.addColumn(cMap);
  // ------------- Column: fieldname --------------------
        cMap = new ColumnMap( "fieldname", tMap);
        cMap.setType( "" );
        cMap.setTorqueType( "VARCHAR" );
        cMap.setUsePrimitive(true);
        cMap.setPrimaryKey(false);
        cMap.setNotNull(false);
        cMap.setJavaName( "Fieldname" );
        cMap.setAutoIncrement(false);
        cMap.setProtected(false);
        cMap.setInheritance("false");
        cMap.setSize( 30 );
        cMap.setPosition(3);
        tMap.addColumn(cMap);
        tMap.setUseInheritance(false);
    }
}
