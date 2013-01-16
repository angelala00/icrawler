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
public class ParserMapBuilder implements MapBuilder
{
    /**
     * The name of this class
     */
    public static final String CLASS_NAME =
        "cn.jc.spider.po.map.ParserMapBuilder";

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

        dbMap.addTable("parser");
        TableMap tMap = dbMap.getTable("parser");
        tMap.setJavaName("Parser");
        tMap.setOMClass( cn.jc.spider.po.Parser.class );
        tMap.setPeerClass( cn.jc.spider.po.ParserPeer.class );
        tMap.setPrimaryKeyMethod(TableMap.NATIVE);
        DB dbAdapter = Torque.getDB("spider_jc");
        if (dbAdapter.getIDMethodType().equals(DB.SEQUENCE))
        {
            tMap.setPrimaryKeyMethodInfo("parser_SEQ");
        }
        else if (dbAdapter.getIDMethodType().equals(DB.AUTO_INCREMENT))
        {
            tMap.setPrimaryKeyMethodInfo("parser");
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
  // ------------- Column: attr --------------------
        cMap = new ColumnMap( "attr", tMap);
        cMap.setType( "" );
        cMap.setTorqueType( "VARCHAR" );
        cMap.setUsePrimitive(true);
        cMap.setPrimaryKey(false);
        cMap.setNotNull(false);
        cMap.setJavaName( "Attr" );
        cMap.setAutoIncrement(false);
        cMap.setProtected(false);
        cMap.setInheritance("false");
        cMap.setSize( 30 );
        cMap.setPosition(3);
        tMap.addColumn(cMap);
  // ------------- Column: pattern --------------------
        cMap = new ColumnMap( "pattern", tMap);
        cMap.setType( "" );
        cMap.setTorqueType( "VARCHAR" );
        cMap.setUsePrimitive(true);
        cMap.setPrimaryKey(false);
        cMap.setNotNull(false);
        cMap.setJavaName( "Pattern" );
        cMap.setAutoIncrement(false);
        cMap.setProtected(false);
        cMap.setInheritance("false");
        cMap.setSize( 100 );
        cMap.setPosition(4);
        tMap.addColumn(cMap);
  // ------------- Column: methodtype --------------------
        cMap = new ColumnMap( "methodtype", tMap);
        cMap.setType( "" );
        cMap.setTorqueType( "VARCHAR" );
        cMap.setUsePrimitive(true);
        cMap.setPrimaryKey(false);
        cMap.setNotNull(false);
        cMap.setJavaName( "Methodtype" );
        cMap.setAutoIncrement(false);
        cMap.setProtected(false);
        cMap.setInheritance("false");
        cMap.setSize( 30 );
        cMap.setPosition(5);
        tMap.addColumn(cMap);
  // ------------- Column: attr_name --------------------
        cMap = new ColumnMap( "attr_name", tMap);
        cMap.setType( "" );
        cMap.setTorqueType( "VARCHAR" );
        cMap.setUsePrimitive(true);
        cMap.setPrimaryKey(false);
        cMap.setNotNull(false);
        cMap.setJavaName( "AttrName" );
        cMap.setAutoIncrement(false);
        cMap.setProtected(false);
        cMap.setInheritance("false");
        cMap.setSize( 30 );
        cMap.setPosition(6);
        tMap.addColumn(cMap);
  // ------------- Column: nodatype --------------------
        cMap = new ColumnMap( "nodatype", tMap);
        cMap.setType( "" );
        cMap.setTorqueType( "VARCHAR" );
        cMap.setUsePrimitive(true);
        cMap.setPrimaryKey(false);
        cMap.setNotNull(false);
        cMap.setJavaName( "Nodatype" );
        cMap.setAutoIncrement(false);
        cMap.setProtected(false);
        cMap.setDescription("节点类型是否为list");
        cMap.setInheritance("false");
        cMap.setSize( 100 );
        cMap.setPosition(7);
        tMap.addColumn(cMap);
  // ------------- Column: pid --------------------
        cMap = new ColumnMap( "pid", tMap);
        cMap.setType( new Integer(0) );
        cMap.setTorqueType( "INTEGER" );
        cMap.setUsePrimitive(true);
        cMap.setPrimaryKey(false);
        cMap.setNotNull(false);
        cMap.setJavaName( "Pid" );
        cMap.setAutoIncrement(false);
        cMap.setProtected(false);
        cMap.setDescription("list节点的子节点，这里是list节点（父节点）的ID");
        cMap.setInheritance("false");
        cMap.setPosition(8);
        tMap.addColumn(cMap);
        tMap.setUseInheritance(false);
    }
}
