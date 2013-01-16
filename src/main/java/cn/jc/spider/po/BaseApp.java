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
 * extended all references should be to App
 */
public abstract class BaseApp extends BaseObject
{
    /** The Peer class */
    private static final AppPeer peer =
        new AppPeer();


    /** The value for the id field */
    private int id;

    /** The value for the appId field */
    private String appId;

    /** The value for the appname field */
    private String appname;

    /** The value for the appnameEn field */
    private String appnameEn;

    /** The value for the description field */
    private String description;

    /** The value for the version field */
    private String version;

    /** The value for the size field */
    private String size;

    /** The value for the sysVer field */
    private String sysVer;

    /** The value for the provider field */
    private String provider;

    /** The value for the downloadUrl field */
    private String downloadUrl;

    /** The value for the imgUrl field */
    private String imgUrl;

    /** The value for the viewUrl field */
    private String viewUrl;

    /** The value for the downloadNum field */
    private String downloadNum;

    /** The value for the author field */
    private String author;

    /** The value for the ratings field */
    private String ratings;

    /** The value for the updatetime field */
    private Date updatetime;

    /** The value for the times field */
    private int times;

    /** The value for the temp field */
    private String temp;


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
     * Get the AppId
     *
     * @return String
     */
    public String getAppId()
    {
        return appId;
    }


    /**
     * Set the value of AppId
     *
     * @param v new value
     */
    public void setAppId(String v) 
    {

        if (!ObjectUtils.equals(this.appId, v))
        {
            this.appId = v;
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
     * Get the AppnameEn
     *
     * @return String
     */
    public String getAppnameEn()
    {
        return appnameEn;
    }


    /**
     * Set the value of AppnameEn
     *
     * @param v new value
     */
    public void setAppnameEn(String v) 
    {

        if (!ObjectUtils.equals(this.appnameEn, v))
        {
            this.appnameEn = v;
            setModified(true);
        }


    }

    /**
     * Get the Description
     *
     * @return String
     */
    public String getDescription()
    {
        return description;
    }


    /**
     * Set the value of Description
     *
     * @param v new value
     */
    public void setDescription(String v) 
    {

        if (!ObjectUtils.equals(this.description, v))
        {
            this.description = v;
            setModified(true);
        }


    }

    /**
     * Get the Version
     *
     * @return String
     */
    public String getVersion()
    {
        return version;
    }


    /**
     * Set the value of Version
     *
     * @param v new value
     */
    public void setVersion(String v) 
    {

        if (!ObjectUtils.equals(this.version, v))
        {
            this.version = v;
            setModified(true);
        }


    }

    /**
     * Get the Size
     *
     * @return String
     */
    public String getSize()
    {
        return size;
    }


    /**
     * Set the value of Size
     *
     * @param v new value
     */
    public void setSize(String v) 
    {

        if (!ObjectUtils.equals(this.size, v))
        {
            this.size = v;
            setModified(true);
        }


    }

    /**
     * Get the SysVer
     *
     * @return String
     */
    public String getSysVer()
    {
        return sysVer;
    }


    /**
     * Set the value of SysVer
     *
     * @param v new value
     */
    public void setSysVer(String v) 
    {

        if (!ObjectUtils.equals(this.sysVer, v))
        {
            this.sysVer = v;
            setModified(true);
        }


    }

    /**
     * Get the Provider
     *
     * @return String
     */
    public String getProvider()
    {
        return provider;
    }


    /**
     * Set the value of Provider
     *
     * @param v new value
     */
    public void setProvider(String v) 
    {

        if (!ObjectUtils.equals(this.provider, v))
        {
            this.provider = v;
            setModified(true);
        }


    }

    /**
     * Get the DownloadUrl
     *
     * @return String
     */
    public String getDownloadUrl()
    {
        return downloadUrl;
    }


    /**
     * Set the value of DownloadUrl
     *
     * @param v new value
     */
    public void setDownloadUrl(String v) 
    {

        if (!ObjectUtils.equals(this.downloadUrl, v))
        {
            this.downloadUrl = v;
            setModified(true);
        }


    }

    /**
     * Get the ImgUrl
     *
     * @return String
     */
    public String getImgUrl()
    {
        return imgUrl;
    }


    /**
     * Set the value of ImgUrl
     *
     * @param v new value
     */
    public void setImgUrl(String v) 
    {

        if (!ObjectUtils.equals(this.imgUrl, v))
        {
            this.imgUrl = v;
            setModified(true);
        }


    }

    /**
     * Get the ViewUrl
     *
     * @return String
     */
    public String getViewUrl()
    {
        return viewUrl;
    }


    /**
     * Set the value of ViewUrl
     *
     * @param v new value
     */
    public void setViewUrl(String v) 
    {

        if (!ObjectUtils.equals(this.viewUrl, v))
        {
            this.viewUrl = v;
            setModified(true);
        }


    }

    /**
     * Get the DownloadNum
     *
     * @return String
     */
    public String getDownloadNum()
    {
        return downloadNum;
    }


    /**
     * Set the value of DownloadNum
     *
     * @param v new value
     */
    public void setDownloadNum(String v) 
    {

        if (!ObjectUtils.equals(this.downloadNum, v))
        {
            this.downloadNum = v;
            setModified(true);
        }


    }

    /**
     * Get the Author
     *
     * @return String
     */
    public String getAuthor()
    {
        return author;
    }


    /**
     * Set the value of Author
     *
     * @param v new value
     */
    public void setAuthor(String v) 
    {

        if (!ObjectUtils.equals(this.author, v))
        {
            this.author = v;
            setModified(true);
        }


    }

    /**
     * Get the Ratings
     *
     * @return String
     */
    public String getRatings()
    {
        return ratings;
    }


    /**
     * Set the value of Ratings
     *
     * @param v new value
     */
    public void setRatings(String v) 
    {

        if (!ObjectUtils.equals(this.ratings, v))
        {
            this.ratings = v;
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
     * Get the Times
     *
     * @return int
     */
    public int getTimes()
    {
        return times;
    }


    /**
     * Set the value of Times
     *
     * @param v new value
     */
    public void setTimes(int v) 
    {

        if (this.times != v)
        {
            this.times = v;
            setModified(true);
        }


    }

    /**
     * Get the Temp
     *
     * @return String
     */
    public String getTemp()
    {
        return temp;
    }


    /**
     * Set the value of Temp
     *
     * @param v new value
     */
    public void setTemp(String v) 
    {

        if (!ObjectUtils.equals(this.temp, v))
        {
            this.temp = v;
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
            fieldNames.add("AppId");
            fieldNames.add("Appname");
            fieldNames.add("AppnameEn");
            fieldNames.add("Description");
            fieldNames.add("Version");
            fieldNames.add("Size");
            fieldNames.add("SysVer");
            fieldNames.add("Provider");
            fieldNames.add("DownloadUrl");
            fieldNames.add("ImgUrl");
            fieldNames.add("ViewUrl");
            fieldNames.add("DownloadNum");
            fieldNames.add("Author");
            fieldNames.add("Ratings");
            fieldNames.add("Updatetime");
            fieldNames.add("Times");
            fieldNames.add("Temp");
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
        if (name.equals("AppId"))
        {
            return getAppId();
        }
        if (name.equals("Appname"))
        {
            return getAppname();
        }
        if (name.equals("AppnameEn"))
        {
            return getAppnameEn();
        }
        if (name.equals("Description"))
        {
            return getDescription();
        }
        if (name.equals("Version"))
        {
            return getVersion();
        }
        if (name.equals("Size"))
        {
            return getSize();
        }
        if (name.equals("SysVer"))
        {
            return getSysVer();
        }
        if (name.equals("Provider"))
        {
            return getProvider();
        }
        if (name.equals("DownloadUrl"))
        {
            return getDownloadUrl();
        }
        if (name.equals("ImgUrl"))
        {
            return getImgUrl();
        }
        if (name.equals("ViewUrl"))
        {
            return getViewUrl();
        }
        if (name.equals("DownloadNum"))
        {
            return getDownloadNum();
        }
        if (name.equals("Author"))
        {
            return getAuthor();
        }
        if (name.equals("Ratings"))
        {
            return getRatings();
        }
        if (name.equals("Updatetime"))
        {
            return getUpdatetime();
        }
        if (name.equals("Times"))
        {
            return new Integer(getTimes());
        }
        if (name.equals("Temp"))
        {
            return getTemp();
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
        if (name.equals("AppId"))
        {
            // Object fields can be null
            if (value != null && ! String.class.isInstance(value))
            {
                throw new IllegalArgumentException("Invalid type of object specified for value in setByName");
            }
            setAppId((String) value);
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
        if (name.equals("AppnameEn"))
        {
            // Object fields can be null
            if (value != null && ! String.class.isInstance(value))
            {
                throw new IllegalArgumentException("Invalid type of object specified for value in setByName");
            }
            setAppnameEn((String) value);
            return true;
        }
        if (name.equals("Description"))
        {
            // Object fields can be null
            if (value != null && ! String.class.isInstance(value))
            {
                throw new IllegalArgumentException("Invalid type of object specified for value in setByName");
            }
            setDescription((String) value);
            return true;
        }
        if (name.equals("Version"))
        {
            // Object fields can be null
            if (value != null && ! String.class.isInstance(value))
            {
                throw new IllegalArgumentException("Invalid type of object specified for value in setByName");
            }
            setVersion((String) value);
            return true;
        }
        if (name.equals("Size"))
        {
            // Object fields can be null
            if (value != null && ! String.class.isInstance(value))
            {
                throw new IllegalArgumentException("Invalid type of object specified for value in setByName");
            }
            setSize((String) value);
            return true;
        }
        if (name.equals("SysVer"))
        {
            // Object fields can be null
            if (value != null && ! String.class.isInstance(value))
            {
                throw new IllegalArgumentException("Invalid type of object specified for value in setByName");
            }
            setSysVer((String) value);
            return true;
        }
        if (name.equals("Provider"))
        {
            // Object fields can be null
            if (value != null && ! String.class.isInstance(value))
            {
                throw new IllegalArgumentException("Invalid type of object specified for value in setByName");
            }
            setProvider((String) value);
            return true;
        }
        if (name.equals("DownloadUrl"))
        {
            // Object fields can be null
            if (value != null && ! String.class.isInstance(value))
            {
                throw new IllegalArgumentException("Invalid type of object specified for value in setByName");
            }
            setDownloadUrl((String) value);
            return true;
        }
        if (name.equals("ImgUrl"))
        {
            // Object fields can be null
            if (value != null && ! String.class.isInstance(value))
            {
                throw new IllegalArgumentException("Invalid type of object specified for value in setByName");
            }
            setImgUrl((String) value);
            return true;
        }
        if (name.equals("ViewUrl"))
        {
            // Object fields can be null
            if (value != null && ! String.class.isInstance(value))
            {
                throw new IllegalArgumentException("Invalid type of object specified for value in setByName");
            }
            setViewUrl((String) value);
            return true;
        }
        if (name.equals("DownloadNum"))
        {
            // Object fields can be null
            if (value != null && ! String.class.isInstance(value))
            {
                throw new IllegalArgumentException("Invalid type of object specified for value in setByName");
            }
            setDownloadNum((String) value);
            return true;
        }
        if (name.equals("Author"))
        {
            // Object fields can be null
            if (value != null && ! String.class.isInstance(value))
            {
                throw new IllegalArgumentException("Invalid type of object specified for value in setByName");
            }
            setAuthor((String) value);
            return true;
        }
        if (name.equals("Ratings"))
        {
            // Object fields can be null
            if (value != null && ! String.class.isInstance(value))
            {
                throw new IllegalArgumentException("Invalid type of object specified for value in setByName");
            }
            setRatings((String) value);
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
        if (name.equals("Times"))
        {
            if (value == null || ! (Integer.class.isInstance(value)))
            {
                throw new IllegalArgumentException("setByName: value parameter was null or not an Integer object.");
            }
            setTimes(((Integer) value).intValue());
            return true;
        }
        if (name.equals("Temp"))
        {
            // Object fields can be null
            if (value != null && ! String.class.isInstance(value))
            {
                throw new IllegalArgumentException("Invalid type of object specified for value in setByName");
            }
            setTemp((String) value);
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
        if (name.equals(AppPeer.ID))
        {
            return new Integer(getId());
        }
        if (name.equals(AppPeer.APP_ID))
        {
            return getAppId();
        }
        if (name.equals(AppPeer.APPNAME))
        {
            return getAppname();
        }
        if (name.equals(AppPeer.APPNAME_EN))
        {
            return getAppnameEn();
        }
        if (name.equals(AppPeer.DESCRIPTION))
        {
            return getDescription();
        }
        if (name.equals(AppPeer.VERSION))
        {
            return getVersion();
        }
        if (name.equals(AppPeer.SIZE))
        {
            return getSize();
        }
        if (name.equals(AppPeer.SYS_VER))
        {
            return getSysVer();
        }
        if (name.equals(AppPeer.PROVIDER))
        {
            return getProvider();
        }
        if (name.equals(AppPeer.DOWNLOAD_URL))
        {
            return getDownloadUrl();
        }
        if (name.equals(AppPeer.IMG_URL))
        {
            return getImgUrl();
        }
        if (name.equals(AppPeer.VIEW_URL))
        {
            return getViewUrl();
        }
        if (name.equals(AppPeer.DOWNLOAD_NUM))
        {
            return getDownloadNum();
        }
        if (name.equals(AppPeer.AUTHOR))
        {
            return getAuthor();
        }
        if (name.equals(AppPeer.RATINGS))
        {
            return getRatings();
        }
        if (name.equals(AppPeer.UPDATETIME))
        {
            return getUpdatetime();
        }
        if (name.equals(AppPeer.TIMES))
        {
            return new Integer(getTimes());
        }
        if (name.equals(AppPeer.TEMP))
        {
            return getTemp();
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
      if (AppPeer.ID.equals(name))
        {
            return setByName("Id", value);
        }
      if (AppPeer.APP_ID.equals(name))
        {
            return setByName("AppId", value);
        }
      if (AppPeer.APPNAME.equals(name))
        {
            return setByName("Appname", value);
        }
      if (AppPeer.APPNAME_EN.equals(name))
        {
            return setByName("AppnameEn", value);
        }
      if (AppPeer.DESCRIPTION.equals(name))
        {
            return setByName("Description", value);
        }
      if (AppPeer.VERSION.equals(name))
        {
            return setByName("Version", value);
        }
      if (AppPeer.SIZE.equals(name))
        {
            return setByName("Size", value);
        }
      if (AppPeer.SYS_VER.equals(name))
        {
            return setByName("SysVer", value);
        }
      if (AppPeer.PROVIDER.equals(name))
        {
            return setByName("Provider", value);
        }
      if (AppPeer.DOWNLOAD_URL.equals(name))
        {
            return setByName("DownloadUrl", value);
        }
      if (AppPeer.IMG_URL.equals(name))
        {
            return setByName("ImgUrl", value);
        }
      if (AppPeer.VIEW_URL.equals(name))
        {
            return setByName("ViewUrl", value);
        }
      if (AppPeer.DOWNLOAD_NUM.equals(name))
        {
            return setByName("DownloadNum", value);
        }
      if (AppPeer.AUTHOR.equals(name))
        {
            return setByName("Author", value);
        }
      if (AppPeer.RATINGS.equals(name))
        {
            return setByName("Ratings", value);
        }
      if (AppPeer.UPDATETIME.equals(name))
        {
            return setByName("Updatetime", value);
        }
      if (AppPeer.TIMES.equals(name))
        {
            return setByName("Times", value);
        }
      if (AppPeer.TEMP.equals(name))
        {
            return setByName("Temp", value);
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
            return getAppId();
        }
        if (pos == 2)
        {
            return getAppname();
        }
        if (pos == 3)
        {
            return getAppnameEn();
        }
        if (pos == 4)
        {
            return getDescription();
        }
        if (pos == 5)
        {
            return getVersion();
        }
        if (pos == 6)
        {
            return getSize();
        }
        if (pos == 7)
        {
            return getSysVer();
        }
        if (pos == 8)
        {
            return getProvider();
        }
        if (pos == 9)
        {
            return getDownloadUrl();
        }
        if (pos == 10)
        {
            return getImgUrl();
        }
        if (pos == 11)
        {
            return getViewUrl();
        }
        if (pos == 12)
        {
            return getDownloadNum();
        }
        if (pos == 13)
        {
            return getAuthor();
        }
        if (pos == 14)
        {
            return getRatings();
        }
        if (pos == 15)
        {
            return getUpdatetime();
        }
        if (pos == 16)
        {
            return new Integer(getTimes());
        }
        if (pos == 17)
        {
            return getTemp();
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
            return setByName("AppId", value);
        }
    if (position == 2)
        {
            return setByName("Appname", value);
        }
    if (position == 3)
        {
            return setByName("AppnameEn", value);
        }
    if (position == 4)
        {
            return setByName("Description", value);
        }
    if (position == 5)
        {
            return setByName("Version", value);
        }
    if (position == 6)
        {
            return setByName("Size", value);
        }
    if (position == 7)
        {
            return setByName("SysVer", value);
        }
    if (position == 8)
        {
            return setByName("Provider", value);
        }
    if (position == 9)
        {
            return setByName("DownloadUrl", value);
        }
    if (position == 10)
        {
            return setByName("ImgUrl", value);
        }
    if (position == 11)
        {
            return setByName("ViewUrl", value);
        }
    if (position == 12)
        {
            return setByName("DownloadNum", value);
        }
    if (position == 13)
        {
            return setByName("Author", value);
        }
    if (position == 14)
        {
            return setByName("Ratings", value);
        }
    if (position == 15)
        {
            return setByName("Updatetime", value);
        }
    if (position == 16)
        {
            return setByName("Times", value);
        }
    if (position == 17)
        {
            return setByName("Temp", value);
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
        save(AppPeer.DATABASE_NAME);
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
                    AppPeer.doInsert((App) this, con);
                    setNew(false);
                }
                else
                {
                    AppPeer.doUpdate((App) this, con);
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
    public App copy() throws TorqueException
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
    public App copy(Connection con) throws TorqueException
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
    public App copy(boolean deepcopy) throws TorqueException
    {
        return copyInto(new App(), deepcopy);
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
    public App copy(boolean deepcopy, Connection con) throws TorqueException
    {
        return copyInto(new App(), deepcopy, con);
    }
  
    /**
     * Fills the copyObj with the contents of this object.
     * The associated objects are also copied and treated as new objects.
     *
     * @param copyObj the object to fill.
     */
    protected App copyInto(App copyObj) throws TorqueException
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
    protected App copyInto(App copyObj, Connection con) throws TorqueException
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
    protected App copyInto(App copyObj, boolean deepcopy) throws TorqueException
    {
        copyObj.setId(id);
        copyObj.setAppId(appId);
        copyObj.setAppname(appname);
        copyObj.setAppnameEn(appnameEn);
        copyObj.setDescription(description);
        copyObj.setVersion(version);
        copyObj.setSize(size);
        copyObj.setSysVer(sysVer);
        copyObj.setProvider(provider);
        copyObj.setDownloadUrl(downloadUrl);
        copyObj.setImgUrl(imgUrl);
        copyObj.setViewUrl(viewUrl);
        copyObj.setDownloadNum(downloadNum);
        copyObj.setAuthor(author);
        copyObj.setRatings(ratings);
        copyObj.setUpdatetime(updatetime);
        copyObj.setTimes(times);
        copyObj.setTemp(temp);

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
    protected App copyInto(App copyObj, boolean deepcopy, Connection con) throws TorqueException
    {
        copyObj.setId(id);
        copyObj.setAppId(appId);
        copyObj.setAppname(appname);
        copyObj.setAppnameEn(appnameEn);
        copyObj.setDescription(description);
        copyObj.setVersion(version);
        copyObj.setSize(size);
        copyObj.setSysVer(sysVer);
        copyObj.setProvider(provider);
        copyObj.setDownloadUrl(downloadUrl);
        copyObj.setImgUrl(imgUrl);
        copyObj.setViewUrl(viewUrl);
        copyObj.setDownloadNum(downloadNum);
        copyObj.setAuthor(author);
        copyObj.setRatings(ratings);
        copyObj.setUpdatetime(updatetime);
        copyObj.setTimes(times);
        copyObj.setTemp(temp);

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
    public AppPeer getPeer()
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
        return AppPeer.getTableMap();
    }


    public String toString()
    {
        StringBuffer str = new StringBuffer();
        str.append("App:\n");
        str.append("Id = ")
           .append(getId())
           .append("\n");
        str.append("AppId = ")
           .append(getAppId())
           .append("\n");
        str.append("Appname = ")
           .append(getAppname())
           .append("\n");
        str.append("AppnameEn = ")
           .append(getAppnameEn())
           .append("\n");
        str.append("Description = ")
           .append(getDescription())
           .append("\n");
        str.append("Version = ")
           .append(getVersion())
           .append("\n");
        str.append("Size = ")
           .append(getSize())
           .append("\n");
        str.append("SysVer = ")
           .append(getSysVer())
           .append("\n");
        str.append("Provider = ")
           .append(getProvider())
           .append("\n");
        str.append("DownloadUrl = ")
           .append(getDownloadUrl())
           .append("\n");
        str.append("ImgUrl = ")
           .append(getImgUrl())
           .append("\n");
        str.append("ViewUrl = ")
           .append(getViewUrl())
           .append("\n");
        str.append("DownloadNum = ")
           .append(getDownloadNum())
           .append("\n");
        str.append("Author = ")
           .append(getAuthor())
           .append("\n");
        str.append("Ratings = ")
           .append(getRatings())
           .append("\n");
        str.append("Updatetime = ")
           .append(getUpdatetime())
           .append("\n");
        str.append("Times = ")
           .append(getTimes())
           .append("\n");
        str.append("Temp = ")
           .append(getTemp())
           .append("\n");
        return(str.toString());
    }
}
