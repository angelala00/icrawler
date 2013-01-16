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
 * extended all references should be to Parser
 */
public abstract class BaseParser extends BaseObject
{
    /** The Peer class */
    private static final ParserPeer peer =
        new ParserPeer();


    /** The value for the id field */
    private int id;

    /** The value for the idTask field */
    private int idTask;

    /** The value for the attr field */
    private String attr;

    /** The value for the pattern field */
    private String pattern;

    /** The value for the methodtype field */
    private String methodtype;

    /** The value for the attrName field */
    private String attrName;

    /** The value for the nodatype field */
    private String nodatype;

    /** The value for the pid field */
    private int pid;


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
     * Get the Attr
     *
     * @return String
     */
    public String getAttr()
    {
        return attr;
    }


    /**
     * Set the value of Attr
     *
     * @param v new value
     */
    public void setAttr(String v) 
    {

        if (!ObjectUtils.equals(this.attr, v))
        {
            this.attr = v;
            setModified(true);
        }


    }

    /**
     * Get the Pattern
     *
     * @return String
     */
    public String getPattern()
    {
        return pattern;
    }


    /**
     * Set the value of Pattern
     *
     * @param v new value
     */
    public void setPattern(String v) 
    {

        if (!ObjectUtils.equals(this.pattern, v))
        {
            this.pattern = v;
            setModified(true);
        }


    }

    /**
     * Get the Methodtype
     *
     * @return String
     */
    public String getMethodtype()
    {
        return methodtype;
    }


    /**
     * Set the value of Methodtype
     *
     * @param v new value
     */
    public void setMethodtype(String v) 
    {

        if (!ObjectUtils.equals(this.methodtype, v))
        {
            this.methodtype = v;
            setModified(true);
        }


    }

    /**
     * Get the AttrName
     *
     * @return String
     */
    public String getAttrName()
    {
        return attrName;
    }


    /**
     * Set the value of AttrName
     *
     * @param v new value
     */
    public void setAttrName(String v) 
    {

        if (!ObjectUtils.equals(this.attrName, v))
        {
            this.attrName = v;
            setModified(true);
        }


    }

    /**
     * Get the Nodatype
     *
     * @return String
     */
    public String getNodatype()
    {
        return nodatype;
    }


    /**
     * Set the value of Nodatype
     *
     * @param v new value
     */
    public void setNodatype(String v) 
    {

        if (!ObjectUtils.equals(this.nodatype, v))
        {
            this.nodatype = v;
            setModified(true);
        }


    }

    /**
     * Get the Pid
     *
     * @return int
     */
    public int getPid()
    {
        return pid;
    }


    /**
     * Set the value of Pid
     *
     * @param v new value
     */
    public void setPid(int v) 
    {

        if (this.pid != v)
        {
            this.pid = v;
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
            fieldNames.add("IdTask");
            fieldNames.add("Attr");
            fieldNames.add("Pattern");
            fieldNames.add("Methodtype");
            fieldNames.add("AttrName");
            fieldNames.add("Nodatype");
            fieldNames.add("Pid");
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
        if (name.equals("Attr"))
        {
            return getAttr();
        }
        if (name.equals("Pattern"))
        {
            return getPattern();
        }
        if (name.equals("Methodtype"))
        {
            return getMethodtype();
        }
        if (name.equals("AttrName"))
        {
            return getAttrName();
        }
        if (name.equals("Nodatype"))
        {
            return getNodatype();
        }
        if (name.equals("Pid"))
        {
            return new Integer(getPid());
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
        if (name.equals("Attr"))
        {
            // Object fields can be null
            if (value != null && ! String.class.isInstance(value))
            {
                throw new IllegalArgumentException("Invalid type of object specified for value in setByName");
            }
            setAttr((String) value);
            return true;
        }
        if (name.equals("Pattern"))
        {
            // Object fields can be null
            if (value != null && ! String.class.isInstance(value))
            {
                throw new IllegalArgumentException("Invalid type of object specified for value in setByName");
            }
            setPattern((String) value);
            return true;
        }
        if (name.equals("Methodtype"))
        {
            // Object fields can be null
            if (value != null && ! String.class.isInstance(value))
            {
                throw new IllegalArgumentException("Invalid type of object specified for value in setByName");
            }
            setMethodtype((String) value);
            return true;
        }
        if (name.equals("AttrName"))
        {
            // Object fields can be null
            if (value != null && ! String.class.isInstance(value))
            {
                throw new IllegalArgumentException("Invalid type of object specified for value in setByName");
            }
            setAttrName((String) value);
            return true;
        }
        if (name.equals("Nodatype"))
        {
            // Object fields can be null
            if (value != null && ! String.class.isInstance(value))
            {
                throw new IllegalArgumentException("Invalid type of object specified for value in setByName");
            }
            setNodatype((String) value);
            return true;
        }
        if (name.equals("Pid"))
        {
            if (value == null || ! (Integer.class.isInstance(value)))
            {
                throw new IllegalArgumentException("setByName: value parameter was null or not an Integer object.");
            }
            setPid(((Integer) value).intValue());
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
        if (name.equals(ParserPeer.ID))
        {
            return new Integer(getId());
        }
        if (name.equals(ParserPeer.ID_TASK))
        {
            return new Integer(getIdTask());
        }
        if (name.equals(ParserPeer.ATTR))
        {
            return getAttr();
        }
        if (name.equals(ParserPeer.PATTERN))
        {
            return getPattern();
        }
        if (name.equals(ParserPeer.METHODTYPE))
        {
            return getMethodtype();
        }
        if (name.equals(ParserPeer.ATTR_NAME))
        {
            return getAttrName();
        }
        if (name.equals(ParserPeer.NODATYPE))
        {
            return getNodatype();
        }
        if (name.equals(ParserPeer.PID))
        {
            return new Integer(getPid());
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
      if (ParserPeer.ID.equals(name))
        {
            return setByName("Id", value);
        }
      if (ParserPeer.ID_TASK.equals(name))
        {
            return setByName("IdTask", value);
        }
      if (ParserPeer.ATTR.equals(name))
        {
            return setByName("Attr", value);
        }
      if (ParserPeer.PATTERN.equals(name))
        {
            return setByName("Pattern", value);
        }
      if (ParserPeer.METHODTYPE.equals(name))
        {
            return setByName("Methodtype", value);
        }
      if (ParserPeer.ATTR_NAME.equals(name))
        {
            return setByName("AttrName", value);
        }
      if (ParserPeer.NODATYPE.equals(name))
        {
            return setByName("Nodatype", value);
        }
      if (ParserPeer.PID.equals(name))
        {
            return setByName("Pid", value);
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
            return getAttr();
        }
        if (pos == 3)
        {
            return getPattern();
        }
        if (pos == 4)
        {
            return getMethodtype();
        }
        if (pos == 5)
        {
            return getAttrName();
        }
        if (pos == 6)
        {
            return getNodatype();
        }
        if (pos == 7)
        {
            return new Integer(getPid());
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
            return setByName("Attr", value);
        }
    if (position == 3)
        {
            return setByName("Pattern", value);
        }
    if (position == 4)
        {
            return setByName("Methodtype", value);
        }
    if (position == 5)
        {
            return setByName("AttrName", value);
        }
    if (position == 6)
        {
            return setByName("Nodatype", value);
        }
    if (position == 7)
        {
            return setByName("Pid", value);
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
        save(ParserPeer.DATABASE_NAME);
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
                    ParserPeer.doInsert((Parser) this, con);
                    setNew(false);
                }
                else
                {
                    ParserPeer.doUpdate((Parser) this, con);
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
    public Parser copy() throws TorqueException
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
    public Parser copy(Connection con) throws TorqueException
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
    public Parser copy(boolean deepcopy) throws TorqueException
    {
        return copyInto(new Parser(), deepcopy);
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
    public Parser copy(boolean deepcopy, Connection con) throws TorqueException
    {
        return copyInto(new Parser(), deepcopy, con);
    }
  
    /**
     * Fills the copyObj with the contents of this object.
     * The associated objects are also copied and treated as new objects.
     *
     * @param copyObj the object to fill.
     */
    protected Parser copyInto(Parser copyObj) throws TorqueException
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
    protected Parser copyInto(Parser copyObj, Connection con) throws TorqueException
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
    protected Parser copyInto(Parser copyObj, boolean deepcopy) throws TorqueException
    {
        copyObj.setId(id);
        copyObj.setIdTask(idTask);
        copyObj.setAttr(attr);
        copyObj.setPattern(pattern);
        copyObj.setMethodtype(methodtype);
        copyObj.setAttrName(attrName);
        copyObj.setNodatype(nodatype);
        copyObj.setPid(pid);

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
    protected Parser copyInto(Parser copyObj, boolean deepcopy, Connection con) throws TorqueException
    {
        copyObj.setId(id);
        copyObj.setIdTask(idTask);
        copyObj.setAttr(attr);
        copyObj.setPattern(pattern);
        copyObj.setMethodtype(methodtype);
        copyObj.setAttrName(attrName);
        copyObj.setNodatype(nodatype);
        copyObj.setPid(pid);

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
    public ParserPeer getPeer()
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
        return ParserPeer.getTableMap();
    }


    public String toString()
    {
        StringBuffer str = new StringBuffer();
        str.append("Parser:\n");
        str.append("Id = ")
           .append(getId())
           .append("\n");
        str.append("IdTask = ")
           .append(getIdTask())
           .append("\n");
        str.append("Attr = ")
           .append(getAttr())
           .append("\n");
        str.append("Pattern = ")
           .append(getPattern())
           .append("\n");
        str.append("Methodtype = ")
           .append(getMethodtype())
           .append("\n");
        str.append("AttrName = ")
           .append(getAttrName())
           .append("\n");
        str.append("Nodatype = ")
           .append(getNodatype())
           .append("\n");
        str.append("Pid = ")
           .append(getPid())
           .append("\n");
        return(str.toString());
    }
}
