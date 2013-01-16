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
 * extended all references should be to Objectattr
 */
public abstract class BaseObjectattr extends BaseObject
{
    /** The Peer class */
    private static final ObjectattrPeer peer =
        new ObjectattrPeer();


    /** The value for the id field */
    private int id;

    /** The value for the website field */
    private String website;

    /** The value for the attrname field */
    private String attrname;

    /** The value for the reg field */
    private String reg;

    /** The value for the index field */
    private int index;

    /** The value for the createtime field */
    private Date createtime;

    /** The value for the updatetime field */
    private Date updatetime;

    /** The value for the operator field */
    private String operator;


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
     * Get the Attrname
     *
     * @return String
     */
    public String getAttrname()
    {
        return attrname;
    }


    /**
     * Set the value of Attrname
     *
     * @param v new value
     */
    public void setAttrname(String v) 
    {

        if (!ObjectUtils.equals(this.attrname, v))
        {
            this.attrname = v;
            setModified(true);
        }


    }

    /**
     * Get the Reg
     *
     * @return String
     */
    public String getReg()
    {
        return reg;
    }


    /**
     * Set the value of Reg
     *
     * @param v new value
     */
    public void setReg(String v) 
    {

        if (!ObjectUtils.equals(this.reg, v))
        {
            this.reg = v;
            setModified(true);
        }


    }

    /**
     * Get the Index
     *
     * @return int
     */
    public int getIndex()
    {
        return index;
    }


    /**
     * Set the value of Index
     *
     * @param v new value
     */
    public void setIndex(int v) 
    {

        if (this.index != v)
        {
            this.index = v;
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

    /**
     * Get the Updatetime
     *
     * @return Date
     */
    public Date getUpdatetime()
    {
        return updatetime;
    }


    /**
     * Set the value of Updatetime
     *
     * @param v new value
     */
    public void setUpdatetime(Date v) 
    {

        if (!ObjectUtils.equals(this.updatetime, v))
        {
            this.updatetime = v;
            setModified(true);
        }


    }

    /**
     * Get the Operator
     *
     * @return String
     */
    public String getOperator()
    {
        return operator;
    }


    /**
     * Set the value of Operator
     *
     * @param v new value
     */
    public void setOperator(String v) 
    {

        if (!ObjectUtils.equals(this.operator, v))
        {
            this.operator = v;
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
            fieldNames.add("Website");
            fieldNames.add("Attrname");
            fieldNames.add("Reg");
            fieldNames.add("Index");
            fieldNames.add("Createtime");
            fieldNames.add("Updatetime");
            fieldNames.add("Operator");
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
        if (name.equals("Attrname"))
        {
            return getAttrname();
        }
        if (name.equals("Reg"))
        {
            return getReg();
        }
        if (name.equals("Index"))
        {
            return new Integer(getIndex());
        }
        if (name.equals("Createtime"))
        {
            return getCreatetime();
        }
        if (name.equals("Updatetime"))
        {
            return getUpdatetime();
        }
        if (name.equals("Operator"))
        {
            return getOperator();
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
        if (name.equals("Attrname"))
        {
            // Object fields can be null
            if (value != null && ! String.class.isInstance(value))
            {
                throw new IllegalArgumentException("Invalid type of object specified for value in setByName");
            }
            setAttrname((String) value);
            return true;
        }
        if (name.equals("Reg"))
        {
            // Object fields can be null
            if (value != null && ! String.class.isInstance(value))
            {
                throw new IllegalArgumentException("Invalid type of object specified for value in setByName");
            }
            setReg((String) value);
            return true;
        }
        if (name.equals("Index"))
        {
            if (value == null || ! (Integer.class.isInstance(value)))
            {
                throw new IllegalArgumentException("setByName: value parameter was null or not an Integer object.");
            }
            setIndex(((Integer) value).intValue());
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
        if (name.equals("Updatetime"))
        {
            // Object fields can be null
            if (value != null && ! Date.class.isInstance(value))
            {
                throw new IllegalArgumentException("Invalid type of object specified for value in setByName");
            }
            setUpdatetime((Date) value);
            return true;
        }
        if (name.equals("Operator"))
        {
            // Object fields can be null
            if (value != null && ! String.class.isInstance(value))
            {
                throw new IllegalArgumentException("Invalid type of object specified for value in setByName");
            }
            setOperator((String) value);
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
        if (name.equals(ObjectattrPeer.ID))
        {
            return new Integer(getId());
        }
        if (name.equals(ObjectattrPeer.WEBSITE))
        {
            return getWebsite();
        }
        if (name.equals(ObjectattrPeer.ATTRNAME))
        {
            return getAttrname();
        }
        if (name.equals(ObjectattrPeer.REG))
        {
            return getReg();
        }
        if (name.equals(ObjectattrPeer.INDEX))
        {
            return new Integer(getIndex());
        }
        if (name.equals(ObjectattrPeer.CREATETIME))
        {
            return getCreatetime();
        }
        if (name.equals(ObjectattrPeer.UPDATETIME))
        {
            return getUpdatetime();
        }
        if (name.equals(ObjectattrPeer.OPERATOR))
        {
            return getOperator();
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
      if (ObjectattrPeer.ID.equals(name))
        {
            return setByName("Id", value);
        }
      if (ObjectattrPeer.WEBSITE.equals(name))
        {
            return setByName("Website", value);
        }
      if (ObjectattrPeer.ATTRNAME.equals(name))
        {
            return setByName("Attrname", value);
        }
      if (ObjectattrPeer.REG.equals(name))
        {
            return setByName("Reg", value);
        }
      if (ObjectattrPeer.INDEX.equals(name))
        {
            return setByName("Index", value);
        }
      if (ObjectattrPeer.CREATETIME.equals(name))
        {
            return setByName("Createtime", value);
        }
      if (ObjectattrPeer.UPDATETIME.equals(name))
        {
            return setByName("Updatetime", value);
        }
      if (ObjectattrPeer.OPERATOR.equals(name))
        {
            return setByName("Operator", value);
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
            return getAttrname();
        }
        if (pos == 3)
        {
            return getReg();
        }
        if (pos == 4)
        {
            return new Integer(getIndex());
        }
        if (pos == 5)
        {
            return getCreatetime();
        }
        if (pos == 6)
        {
            return getUpdatetime();
        }
        if (pos == 7)
        {
            return getOperator();
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
            return setByName("Attrname", value);
        }
    if (position == 3)
        {
            return setByName("Reg", value);
        }
    if (position == 4)
        {
            return setByName("Index", value);
        }
    if (position == 5)
        {
            return setByName("Createtime", value);
        }
    if (position == 6)
        {
            return setByName("Updatetime", value);
        }
    if (position == 7)
        {
            return setByName("Operator", value);
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
        save(ObjectattrPeer.DATABASE_NAME);
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
                    ObjectattrPeer.doInsert((Objectattr) this, con);
                    setNew(false);
                }
                else
                {
                    ObjectattrPeer.doUpdate((Objectattr) this, con);
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
    public Objectattr copy() throws TorqueException
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
    public Objectattr copy(Connection con) throws TorqueException
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
    public Objectattr copy(boolean deepcopy) throws TorqueException
    {
        return copyInto(new Objectattr(), deepcopy);
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
    public Objectattr copy(boolean deepcopy, Connection con) throws TorqueException
    {
        return copyInto(new Objectattr(), deepcopy, con);
    }
  
    /**
     * Fills the copyObj with the contents of this object.
     * The associated objects are also copied and treated as new objects.
     *
     * @param copyObj the object to fill.
     */
    protected Objectattr copyInto(Objectattr copyObj) throws TorqueException
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
    protected Objectattr copyInto(Objectattr copyObj, Connection con) throws TorqueException
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
    protected Objectattr copyInto(Objectattr copyObj, boolean deepcopy) throws TorqueException
    {
        copyObj.setId(id);
        copyObj.setWebsite(website);
        copyObj.setAttrname(attrname);
        copyObj.setReg(reg);
        copyObj.setIndex(index);
        copyObj.setCreatetime(createtime);
        copyObj.setUpdatetime(updatetime);
        copyObj.setOperator(operator);

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
    protected Objectattr copyInto(Objectattr copyObj, boolean deepcopy, Connection con) throws TorqueException
    {
        copyObj.setId(id);
        copyObj.setWebsite(website);
        copyObj.setAttrname(attrname);
        copyObj.setReg(reg);
        copyObj.setIndex(index);
        copyObj.setCreatetime(createtime);
        copyObj.setUpdatetime(updatetime);
        copyObj.setOperator(operator);

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
    public ObjectattrPeer getPeer()
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
        return ObjectattrPeer.getTableMap();
    }


    public String toString()
    {
        StringBuffer str = new StringBuffer();
        str.append("Objectattr:\n");
        str.append("Id = ")
           .append(getId())
           .append("\n");
        str.append("Website = ")
           .append(getWebsite())
           .append("\n");
        str.append("Attrname = ")
           .append(getAttrname())
           .append("\n");
        str.append("Reg = ")
           .append(getReg())
           .append("\n");
        str.append("Index = ")
           .append(getIndex())
           .append("\n");
        str.append("Createtime = ")
           .append(getCreatetime())
           .append("\n");
        str.append("Updatetime = ")
           .append(getUpdatetime())
           .append("\n");
        str.append("Operator = ")
           .append(getOperator())
           .append("\n");
        return(str.toString());
    }
}
