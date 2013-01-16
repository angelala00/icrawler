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
 * extended all references should be to Unvisitedurl
 */
public abstract class BaseUnvisitedurl extends BaseObject
{
    /** The Peer class */
    private static final UnvisitedurlPeer peer =
        new UnvisitedurlPeer();


    /** The value for the id field */
    private int id;

    /** The value for the idTask field */
    private int idTask;

    /** The value for the website field */
    private String website;

    /** The value for the url field */
    private String url;

    /** The value for the timetime field */
    private int timetime = 0;

    /** The value for the fuzhubiaoshiid field */
    private String fuzhubiaoshiid;


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
     * Get the IdTask
     *
     * @return int
     */
    public int getIdTask()
    {
        return idTask;
    }


    /**
     * Set the value of IdTask
     *
     * @param v new value
     */
    public void setIdTask(int v) 
    {

        if (this.idTask != v)
        {
            this.idTask = v;
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
    public void setWebsite(String v) throws TorqueException
    {

        if (!ObjectUtils.equals(this.website, v))
        {
            this.website = v;
            setModified(true);
        }


        if (aSite != null && !ObjectUtils.equals(aSite.getWebsite(), v))
        {
            aSite = null;
        }

    }

    /**
     * Get the Url
     *
     * @return String
     */
    public String getUrl()
    {
        return url;
    }


    /**
     * Set the value of Url
     *
     * @param v new value
     */
    public void setUrl(String v) 
    {

        if (!ObjectUtils.equals(this.url, v))
        {
            this.url = v;
            setModified(true);
        }


    }

    /**
     * Get the Timetime
     *
     * @return int
     */
    public int getTimetime()
    {
        return timetime;
    }


    /**
     * Set the value of Timetime
     *
     * @param v new value
     */
    public void setTimetime(int v) 
    {

        if (this.timetime != v)
        {
            this.timetime = v;
            setModified(true);
        }


    }

    /**
     * Get the Fuzhubiaoshiid
     *
     * @return String
     */
    public String getFuzhubiaoshiid()
    {
        return fuzhubiaoshiid;
    }


    /**
     * Set the value of Fuzhubiaoshiid
     *
     * @param v new value
     */
    public void setFuzhubiaoshiid(String v) 
    {

        if (!ObjectUtils.equals(this.fuzhubiaoshiid, v))
        {
            this.fuzhubiaoshiid = v;
            setModified(true);
        }


    }

    



    private Site aSite;

    /**
     * Declares an association between this object and a Site object
     *
     * @param v Site
     * @throws TorqueException
     */
    public void setSite(Site v) throws TorqueException
    {
        if (v == null)
        {
            setWebsite((String) null);
        }
        else
        {
            setWebsite(v.getWebsite());
        }
        aSite = v;
    }


    /**
     * Returns the associated Site object.
     * If it was not retrieved before, the object is retrieved from
     * the database
     *
     * @return the associated Site object
     * @throws TorqueException
     */
    public Site getSite()
        throws TorqueException
    {
        if (aSite == null && (!ObjectUtils.equals(this.website, null)))
        {
            aSite = SitePeer.retrieveByPK(SimpleKey.keyFor(this.website));
        }
        return aSite;
    }

    /**
     * Return the associated Site object
     * If it was not retrieved before, the object is retrieved from
     * the database using the passed connection
     *
     * @param connection the connection used to retrieve the associated object
     *        from the database, if it was not retrieved before
     * @return the associated Site object
     * @throws TorqueException
     */
    public Site getSite(Connection connection)
        throws TorqueException
    {
        if (aSite == null && (!ObjectUtils.equals(this.website, null)))
        {
            aSite = SitePeer.retrieveByPK(SimpleKey.keyFor(this.website), connection);
        }
        return aSite;
    }

    /**
     * Provides convenient way to set a relationship based on a
     * ObjectKey, for example
     * <code>bar.setFooKey(foo.getPrimaryKey())</code>
     *
     */
    public void setSiteKey(ObjectKey key) throws TorqueException
    {

        setWebsite(key.toString());
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
            fieldNames.add("IdTask");
            fieldNames.add("Website");
            fieldNames.add("Url");
            fieldNames.add("Timetime");
            fieldNames.add("Fuzhubiaoshiid");
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
        if (name.equals("IdTask"))
        {
            return new Integer(getIdTask());
        }
        if (name.equals("Website"))
        {
            return getWebsite();
        }
        if (name.equals("Url"))
        {
            return getUrl();
        }
        if (name.equals("Timetime"))
        {
            return new Integer(getTimetime());
        }
        if (name.equals("Fuzhubiaoshiid"))
        {
            return getFuzhubiaoshiid();
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
        if (name.equals("IdTask"))
        {
            if (value == null || ! (Integer.class.isInstance(value)))
            {
                throw new IllegalArgumentException("setByName: value parameter was null or not an Integer object.");
            }
            setIdTask(((Integer) value).intValue());
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
        if (name.equals("Url"))
        {
            // Object fields can be null
            if (value != null && ! String.class.isInstance(value))
            {
                throw new IllegalArgumentException("Invalid type of object specified for value in setByName");
            }
            setUrl((String) value);
            return true;
        }
        if (name.equals("Timetime"))
        {
            if (value == null || ! (Integer.class.isInstance(value)))
            {
                throw new IllegalArgumentException("setByName: value parameter was null or not an Integer object.");
            }
            setTimetime(((Integer) value).intValue());
            return true;
        }
        if (name.equals("Fuzhubiaoshiid"))
        {
            // Object fields can be null
            if (value != null && ! String.class.isInstance(value))
            {
                throw new IllegalArgumentException("Invalid type of object specified for value in setByName");
            }
            setFuzhubiaoshiid((String) value);
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
        if (name.equals(UnvisitedurlPeer.ID))
        {
            return new Integer(getId());
        }
        if (name.equals(UnvisitedurlPeer.ID_TASK))
        {
            return new Integer(getIdTask());
        }
        if (name.equals(UnvisitedurlPeer.WEBSITE))
        {
            return getWebsite();
        }
        if (name.equals(UnvisitedurlPeer.URL))
        {
            return getUrl();
        }
        if (name.equals(UnvisitedurlPeer.TIMETIME))
        {
            return new Integer(getTimetime());
        }
        if (name.equals(UnvisitedurlPeer.FUZHUBIAOSHIID))
        {
            return getFuzhubiaoshiid();
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
      if (UnvisitedurlPeer.ID.equals(name))
        {
            return setByName("Id", value);
        }
      if (UnvisitedurlPeer.ID_TASK.equals(name))
        {
            return setByName("IdTask", value);
        }
      if (UnvisitedurlPeer.WEBSITE.equals(name))
        {
            return setByName("Website", value);
        }
      if (UnvisitedurlPeer.URL.equals(name))
        {
            return setByName("Url", value);
        }
      if (UnvisitedurlPeer.TIMETIME.equals(name))
        {
            return setByName("Timetime", value);
        }
      if (UnvisitedurlPeer.FUZHUBIAOSHIID.equals(name))
        {
            return setByName("Fuzhubiaoshiid", value);
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
            return new Integer(getIdTask());
        }
        if (pos == 2)
        {
            return getWebsite();
        }
        if (pos == 3)
        {
            return getUrl();
        }
        if (pos == 4)
        {
            return new Integer(getTimetime());
        }
        if (pos == 5)
        {
            return getFuzhubiaoshiid();
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
            return setByName("IdTask", value);
        }
    if (position == 2)
        {
            return setByName("Website", value);
        }
    if (position == 3)
        {
            return setByName("Url", value);
        }
    if (position == 4)
        {
            return setByName("Timetime", value);
        }
    if (position == 5)
        {
            return setByName("Fuzhubiaoshiid", value);
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
        save(UnvisitedurlPeer.DATABASE_NAME);
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
                    UnvisitedurlPeer.doInsert((Unvisitedurl) this, con);
                    setNew(false);
                }
                else
                {
                    UnvisitedurlPeer.doUpdate((Unvisitedurl) this, con);
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
    public Unvisitedurl copy() throws TorqueException
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
    public Unvisitedurl copy(Connection con) throws TorqueException
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
    public Unvisitedurl copy(boolean deepcopy) throws TorqueException
    {
        return copyInto(new Unvisitedurl(), deepcopy);
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
    public Unvisitedurl copy(boolean deepcopy, Connection con) throws TorqueException
    {
        return copyInto(new Unvisitedurl(), deepcopy, con);
    }
  
    /**
     * Fills the copyObj with the contents of this object.
     * The associated objects are also copied and treated as new objects.
     *
     * @param copyObj the object to fill.
     */
    protected Unvisitedurl copyInto(Unvisitedurl copyObj) throws TorqueException
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
    protected Unvisitedurl copyInto(Unvisitedurl copyObj, Connection con) throws TorqueException
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
    protected Unvisitedurl copyInto(Unvisitedurl copyObj, boolean deepcopy) throws TorqueException
    {
        copyObj.setId(id);
        copyObj.setIdTask(idTask);
        copyObj.setWebsite(website);
        copyObj.setUrl(url);
        copyObj.setTimetime(timetime);
        copyObj.setFuzhubiaoshiid(fuzhubiaoshiid);

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
    protected Unvisitedurl copyInto(Unvisitedurl copyObj, boolean deepcopy, Connection con) throws TorqueException
    {
        copyObj.setId(id);
        copyObj.setIdTask(idTask);
        copyObj.setWebsite(website);
        copyObj.setUrl(url);
        copyObj.setTimetime(timetime);
        copyObj.setFuzhubiaoshiid(fuzhubiaoshiid);

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
    public UnvisitedurlPeer getPeer()
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
        return UnvisitedurlPeer.getTableMap();
    }


    public String toString()
    {
        StringBuffer str = new StringBuffer();
        str.append("Unvisitedurl:\n");
        str.append("Id = ")
           .append(getId())
           .append("\n");
        str.append("IdTask = ")
           .append(getIdTask())
           .append("\n");
        str.append("Website = ")
           .append(getWebsite())
           .append("\n");
        str.append("Url = ")
           .append(getUrl())
           .append("\n");
        str.append("Timetime = ")
           .append(getTimetime())
           .append("\n");
        str.append("Fuzhubiaoshiid = ")
           .append(getFuzhubiaoshiid())
           .append("\n");
        return(str.toString());
    }
}
