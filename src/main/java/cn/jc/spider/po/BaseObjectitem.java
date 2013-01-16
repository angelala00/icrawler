package cn.jc.spider.po;


import java.math.BigDecimal;
import java.sql.Connection;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Date;
import java.util.List;

import org.apache.commons.lang.ObjectUtils;
import org.apache.torque.TorqueException;
import org.apache.torque.map.TableMap;
import org.apache.torque.om.BaseObject;
import org.apache.torque.om.ComboKey;
import org.apache.torque.om.DateKey;
import org.apache.torque.om.NumberKey;
import org.apache.torque.om.ObjectKey;
import org.apache.torque.om.SimpleKey;
import org.apache.torque.om.StringKey;
import org.apache.torque.om.Persistent;
import org.apache.torque.util.Criteria;
import org.apache.torque.util.Transaction;





/**
 * You should not use this class directly.  It should not even be
 * extended all references should be to Objectitem
 */
public abstract class BaseObjectitem extends BaseObject
{
    /** The Peer class */
    private static final ObjectitemPeer peer =
        new ObjectitemPeer();


    /** The value for the id field */
    private int id;

    /** The value for the website field */
    private String website;

    /** The value for the appname field */
    private String appname;

    /** The value for the appsize field */
    private String appsize;

    /** The value for the appurl field */
    private String appurl;

    /** The value for the imgurl field */
    private String imgurl;

    /** The value for the appdesc field */
    private String appdesc;

    /** The value for the createtime field */
    private Date createtime;


    /**
     * Get the Id
     *
     * @return int
     */
    public int getId()
    {
        return id;
    }


    /**
     * Set the value of Id
     *
     * @param v new value
     */
    public void setId(int v) 
    {

        if (this.id != v)
        {
            this.id = v;
            setModified(true);
        }


    }

    /**
     * Get the Website
     *
     * @return String
     */
    public String getWebsite()
    {
        return website;
    }


    /**
     * Set the value of Website
     *
     * @param v new value
     */
    public void setWebsite(String v) 
    {

        if (!ObjectUtils.equals(this.website, v))
        {
            this.website = v;
            setModified(true);
        }


    }

    /**
     * Get the Appname
     *
     * @return String
     */
    public String getAppname()
    {
        return appname;
    }


    /**
     * Set the value of Appname
     *
     * @param v new value
     */
    public void setAppname(String v) 
    {

        if (!ObjectUtils.equals(this.appname, v))
        {
            this.appname = v;
            setModified(true);
        }


    }

    /**
     * Get the Appsize
     *
     * @return String
     */
    public String getAppsize()
    {
        return appsize;
    }


    /**
     * Set the value of Appsize
     *
     * @param v new value
     */
    public void setAppsize(String v) 
    {

        if (!ObjectUtils.equals(this.appsize, v))
        {
            this.appsize = v;
            setModified(true);
        }


    }

    /**
     * Get the Appurl
     *
     * @return String
     */
    public String getAppurl()
    {
        return appurl;
    }


    /**
     * Set the value of Appurl
     *
     * @param v new value
     */
    public void setAppurl(String v) 
    {

        if (!ObjectUtils.equals(this.appurl, v))
        {
            this.appurl = v;
            setModified(true);
        }


    }

    /**
     * Get the Imgurl
     *
     * @return String
     */
    public String getImgurl()
    {
        return imgurl;
    }


    /**
     * Set the value of Imgurl
     *
     * @param v new value
     */
    public void setImgurl(String v) 
    {

        if (!ObjectUtils.equals(this.imgurl, v))
        {
            this.imgurl = v;
            setModified(true);
        }


    }

    /**
     * Get the Appdesc
     *
     * @return String
     */
    public String getAppdesc()
    {
        return appdesc;
    }


    /**
     * Set the value of Appdesc
     *
     * @param v new value
     */
    public void setAppdesc(String v) 
    {

        if (!ObjectUtils.equals(this.appdesc, v))
        {
            this.appdesc = v;
            setModified(true);
        }


    }

    /**
     * Get the Createtime
     *
     * @return Date
     */
    public Date getCreatetime()
    {
        return createtime;
    }


    /**
     * Set the value of Createtime
     *
     * @param v new value
     */
    public void setCreatetime(Date v) 
    {

        if (!ObjectUtils.equals(this.createtime, v))
        {
            this.createtime = v;
            setModified(true);
        }


    }

       
        
    private static List fieldNames = null;

    /**
     * Generate a list of field names.
     *
     * @return a list of field names
     */
    public static synchronized List getFieldNames()
    {
        if (fieldNames == null)
        {
            fieldNames = new ArrayList();
            fieldNames.add("Id");
            fieldNames.add("Website");
            fieldNames.add("Appname");
            fieldNames.add("Appsize");
            fieldNames.add("Appurl");
            fieldNames.add("Imgurl");
            fieldNames.add("Appdesc");
            fieldNames.add("Createtime");
            fieldNames = Collections.unmodifiableList(fieldNames);
        }
        return fieldNames;
    }

    /**
     * Retrieves a field from the object by field (Java) name passed in as a String.
     *
     * @param name field name
     * @return value
     */
    public Object getByName(String name)
    {
        if (name.equals("Id"))
        {
            return new Integer(getId());
        }
        if (name.equals("Website"))
        {
            return getWebsite();
        }
        if (name.equals("Appname"))
        {
            return getAppname();
        }
        if (name.equals("Appsize"))
        {
            return getAppsize();
        }
        if (name.equals("Appurl"))
        {
            return getAppurl();
        }
        if (name.equals("Imgurl"))
        {
            return getImgurl();
        }
        if (name.equals("Appdesc"))
        {
            return getAppdesc();
        }
        if (name.equals("Createtime"))
        {
            return getCreatetime();
        }
        return null;
    }

    /**
     * Set a field in the object by field (Java) name.
     *
     * @param name field name
     * @param value field value
     * @return True if value was set, false if not (invalid name / protected field).
     * @throws IllegalArgumentException if object type of value does not match field object type.
     * @throws TorqueException If a problem occurs with the set[Field] method.
     */
    public boolean setByName(String name, Object value )
        throws TorqueException, IllegalArgumentException
    {
        if (name.equals("Id"))
        {
            if (value == null || ! (Integer.class.isInstance(value)))
            {
                throw new IllegalArgumentException("setByName: value parameter was null or not an Integer object.");
            }
            setId(((Integer) value).intValue());
            return true;
        }
        if (name.equals("Website"))
        {
            // Object fields can be null
            if (value != null && ! String.class.isInstance(value))
            {
                throw new IllegalArgumentException("Invalid type of object specified for value in setByName");
            }
            setWebsite((String) value);
            return true;
        }
        if (name.equals("Appname"))
        {
            // Object fields can be null
            if (value != null && ! String.class.isInstance(value))
            {
                throw new IllegalArgumentException("Invalid type of object specified for value in setByName");
            }
            setAppname((String) value);
            return true;
        }
        if (name.equals("Appsize"))
        {
            // Object fields can be null
            if (value != null && ! String.class.isInstance(value))
            {
                throw new IllegalArgumentException("Invalid type of object specified for value in setByName");
            }
            setAppsize((String) value);
            return true;
        }
        if (name.equals("Appurl"))
        {
            // Object fields can be null
            if (value != null && ! String.class.isInstance(value))
            {
                throw new IllegalArgumentException("Invalid type of object specified for value in setByName");
            }
            setAppurl((String) value);
            return true;
        }
        if (name.equals("Imgurl"))
        {
            // Object fields can be null
            if (value != null && ! String.class.isInstance(value))
            {
                throw new IllegalArgumentException("Invalid type of object specified for value in setByName");
            }
            setImgurl((String) value);
            return true;
        }
        if (name.equals("Appdesc"))
        {
            // Object fields can be null
            if (value != null && ! String.class.isInstance(value))
            {
                throw new IllegalArgumentException("Invalid type of object specified for value in setByName");
            }
            setAppdesc((String) value);
            return true;
        }
        if (name.equals("Createtime"))
        {
            // Object fields can be null
            if (value != null && ! Date.class.isInstance(value))
            {
                throw new IllegalArgumentException("Invalid type of object specified for value in setByName");
            }
            setCreatetime((Date) value);
            return true;
        }
        return false;
    }

    /**
     * Retrieves a field from the object by name passed in
     * as a String.  The String must be one of the static
     * Strings defined in this Class' Peer.
     *
     * @param name peer name
     * @return value
     */
    public Object getByPeerName(String name)
    {
        if (name.equals(ObjectitemPeer.ID))
        {
            return new Integer(getId());
        }
        if (name.equals(ObjectitemPeer.WEBSITE))
        {
            return getWebsite();
        }
        if (name.equals(ObjectitemPeer.APPNAME))
        {
            return getAppname();
        }
        if (name.equals(ObjectitemPeer.APPSIZE))
        {
            return getAppsize();
        }
        if (name.equals(ObjectitemPeer.APPURL))
        {
            return getAppurl();
        }
        if (name.equals(ObjectitemPeer.IMGURL))
        {
            return getImgurl();
        }
        if (name.equals(ObjectitemPeer.APPDESC))
        {
            return getAppdesc();
        }
        if (name.equals(ObjectitemPeer.CREATETIME))
        {
            return getCreatetime();
        }
        return null;
    }

    /**
     * Set field values by Peer Field Name
     *
     * @param name field name
     * @param value field value
     * @return True if value was set, false if not (invalid name / protected field).
     * @throws IllegalArgumentException if object type of value does not match field object type.
     * @throws TorqueException If a problem occurs with the set[Field] method.
     */
    public boolean setByPeerName(String name, Object value)
        throws TorqueException, IllegalArgumentException
    {
      if (ObjectitemPeer.ID.equals(name))
        {
            return setByName("Id", value);
        }
      if (ObjectitemPeer.WEBSITE.equals(name))
        {
            return setByName("Website", value);
        }
      if (ObjectitemPeer.APPNAME.equals(name))
        {
            return setByName("Appname", value);
        }
      if (ObjectitemPeer.APPSIZE.equals(name))
        {
            return setByName("Appsize", value);
        }
      if (ObjectitemPeer.APPURL.equals(name))
        {
            return setByName("Appurl", value);
        }
      if (ObjectitemPeer.IMGURL.equals(name))
        {
            return setByName("Imgurl", value);
        }
      if (ObjectitemPeer.APPDESC.equals(name))
        {
            return setByName("Appdesc", value);
        }
      if (ObjectitemPeer.CREATETIME.equals(name))
        {
            return setByName("Createtime", value);
        }
        return false;
    }

    /**
     * Retrieves a field from the object by Position as specified
     * in the xml schema.  Zero-based.
     *
     * @param pos position in xml schema
     * @return value
     */
    public Object getByPosition(int pos)
    {
        if (pos == 0)
        {
            return new Integer(getId());
        }
        if (pos == 1)
        {
            return getWebsite();
        }
        if (pos == 2)
        {
            return getAppname();
        }
        if (pos == 3)
        {
            return getAppsize();
        }
        if (pos == 4)
        {
            return getAppurl();
        }
        if (pos == 5)
        {
            return getImgurl();
        }
        if (pos == 6)
        {
            return getAppdesc();
        }
        if (pos == 7)
        {
            return getCreatetime();
        }
        return null;
    }

    /**
     * Set field values by its position (zero based) in the XML schema.
     *
     * @param position The field position
     * @param value field value
     * @return True if value was set, false if not (invalid position / protected field).
     * @throws IllegalArgumentException if object type of value does not match field object type.
     * @throws TorqueException If a problem occurs with the set[Field] method.
     */
    public boolean setByPosition(int position, Object value)
        throws TorqueException, IllegalArgumentException
    {
    if (position == 0)
        {
            return setByName("Id", value);
        }
    if (position == 1)
        {
            return setByName("Website", value);
        }
    if (position == 2)
        {
            return setByName("Appname", value);
        }
    if (position == 3)
        {
            return setByName("Appsize", value);
        }
    if (position == 4)
        {
            return setByName("Appurl", value);
        }
    if (position == 5)
        {
            return setByName("Imgurl", value);
        }
    if (position == 6)
        {
            return setByName("Appdesc", value);
        }
    if (position == 7)
        {
            return setByName("Createtime", value);
        }
        return false;
    }
     
    /**
     * Stores the object in the database.  If the object is new,
     * it inserts it; otherwise an update is performed.
     *
     * @throws Exception
     */
    public void save() throws Exception
    {
        save(ObjectitemPeer.DATABASE_NAME);
    }

    /**
     * Stores the object in the database.  If the object is new,
     * it inserts it; otherwise an update is performed.
     * Note: this code is here because the method body is
     * auto-generated conditionally and therefore needs to be
     * in this file instead of in the super class, BaseObject.
     *
     * @param dbName
     * @throws TorqueException
     */
    public void save(String dbName) throws TorqueException
    {
        Connection con = null;
        try
        {
            con = Transaction.begin(dbName);
            save(con);
            Transaction.commit(con);
        }
        catch(TorqueException e)
        {
            Transaction.safeRollback(con);
            throw e;
        }
    }

    /** flag to prevent endless save loop, if this object is referenced
        by another object which falls in this transaction. */
    private boolean alreadyInSave = false;
    /**
     * Stores the object in the database.  If the object is new,
     * it inserts it; otherwise an update is performed.  This method
     * is meant to be used as part of a transaction, otherwise use
     * the save() method and the connection details will be handled
     * internally
     *
     * @param con
     * @throws TorqueException
     */
    public void save(Connection con) throws TorqueException
    {
        if (!alreadyInSave)
        {
            alreadyInSave = true;



            // If this object has been modified, then save it to the database.
            if (isModified())
            {
                if (isNew())
                {
                    ObjectitemPeer.doInsert((Objectitem) this, con);
                    setNew(false);
                }
                else
                {
                    ObjectitemPeer.doUpdate((Objectitem) this, con);
                }
            }

            alreadyInSave = false;
        }
    }


    /**
     * Set the PrimaryKey using ObjectKey.
     *
     * @param key id ObjectKey
     */
    public void setPrimaryKey(ObjectKey key)
        
    {
        setId(((NumberKey) key).intValue());
    }

    /**
     * Set the PrimaryKey using a String.
     *
     * @param key
     */
    public void setPrimaryKey(String key) 
    {
        setId(Integer.parseInt(key));
    }


    /**
     * returns an id that differentiates this object from others
     * of its class.
     */
    public ObjectKey getPrimaryKey()
    {
        return SimpleKey.keyFor(getId());
    }
 

    /**
     * Makes a copy of this object.
     * It creates a new object filling in the simple attributes.
     * It then fills all the association collections and sets the
     * related objects to isNew=true.
     */
    public Objectitem copy() throws TorqueException
    {
        return copy(true);
    }

    /**
     * Makes a copy of this object using connection.
     * It creates a new object filling in the simple attributes.
     * It then fills all the association collections and sets the
     * related objects to isNew=true.
     *
     * @param con the database connection to read associated objects.
     */
    public Objectitem copy(Connection con) throws TorqueException
    {
        return copy(true, con);
    }

    /**
     * Makes a copy of this object.
     * It creates a new object filling in the simple attributes.
     * If the parameter deepcopy is true, it then fills all the
     * association collections and sets the related objects to
     * isNew=true.
     *
     * @param deepcopy whether to copy the associated objects.
     */
    public Objectitem copy(boolean deepcopy) throws TorqueException
    {
        return copyInto(new Objectitem(), deepcopy);
    }

    /**
     * Makes a copy of this object using connection.
     * It creates a new object filling in the simple attributes.
     * If the parameter deepcopy is true, it then fills all the
     * association collections and sets the related objects to
     * isNew=true.
     *
     * @param deepcopy whether to copy the associated objects.
     * @param con the database connection to read associated objects.
     */
    public Objectitem copy(boolean deepcopy, Connection con) throws TorqueException
    {
        return copyInto(new Objectitem(), deepcopy, con);
    }
  
    /**
     * Fills the copyObj with the contents of this object.
     * The associated objects are also copied and treated as new objects.
     *
     * @param copyObj the object to fill.
     */
    protected Objectitem copyInto(Objectitem copyObj) throws TorqueException
    {
        return copyInto(copyObj, true);
    }

  
    /**
     * Fills the copyObj with the contents of this object using connection.
     * The associated objects are also copied and treated as new objects.
     *
     * @param copyObj the object to fill.
     * @param con the database connection to read associated objects.
     */
    protected Objectitem copyInto(Objectitem copyObj, Connection con) throws TorqueException
    {
        return copyInto(copyObj, true, con);
    }
  
    /**
     * Fills the copyObj with the contents of this object.
     * If deepcopy is true, The associated objects are also copied
     * and treated as new objects.
     *
     * @param copyObj the object to fill.
     * @param deepcopy whether the associated objects should be copied.
     */
    protected Objectitem copyInto(Objectitem copyObj, boolean deepcopy) throws TorqueException
    {
        copyObj.setId(id);
        copyObj.setWebsite(website);
        copyObj.setAppname(appname);
        copyObj.setAppsize(appsize);
        copyObj.setAppurl(appurl);
        copyObj.setImgurl(imgurl);
        copyObj.setAppdesc(appdesc);
        copyObj.setCreatetime(createtime);

        copyObj.setId( 0);

        if (deepcopy)
        {
        }
        return copyObj;
    }
        
    
    /**
     * Fills the copyObj with the contents of this object using connection.
     * If deepcopy is true, The associated objects are also copied
     * and treated as new objects.
     *
     * @param copyObj the object to fill.
     * @param deepcopy whether the associated objects should be copied.
     * @param con the database connection to read associated objects.
     */
    protected Objectitem copyInto(Objectitem copyObj, boolean deepcopy, Connection con) throws TorqueException
    {
        copyObj.setId(id);
        copyObj.setWebsite(website);
        copyObj.setAppname(appname);
        copyObj.setAppsize(appsize);
        copyObj.setAppurl(appurl);
        copyObj.setImgurl(imgurl);
        copyObj.setAppdesc(appdesc);
        copyObj.setCreatetime(createtime);

        copyObj.setId( 0);

        if (deepcopy)
        {
        }
        return copyObj;
    }
    
    

    /**
     * returns a peer instance associated with this om.  Since Peer classes
     * are not to have any instance attributes, this method returns the
     * same instance for all member of this class. The method could therefore
     * be static, but this would prevent one from overriding the behavior.
     */
    public ObjectitemPeer getPeer()
    {
        return peer;
    }

    /**
     * Retrieves the TableMap object related to this Table data without
     * compiler warnings of using getPeer().getTableMap().
     *
     * @return The associated TableMap object.
     */
    public TableMap getTableMap() throws TorqueException
    {
        return ObjectitemPeer.getTableMap();
    }


    public String toString()
    {
        StringBuffer str = new StringBuffer();
        str.append("Objectitem:\n");
        str.append("Id = ")
           .append(getId())
           .append("\n");
        str.append("Website = ")
           .append(getWebsite())
           .append("\n");
        str.append("Appname = ")
           .append(getAppname())
           .append("\n");
        str.append("Appsize = ")
           .append(getAppsize())
           .append("\n");
        str.append("Appurl = ")
           .append(getAppurl())
           .append("\n");
        str.append("Imgurl = ")
           .append(getImgurl())
           .append("\n");
        str.append("Appdesc = ")
           .append(getAppdesc())
           .append("\n");
        str.append("Createtime = ")
           .append(getCreatetime())
           .append("\n");
        return(str.toString());
    }
}
