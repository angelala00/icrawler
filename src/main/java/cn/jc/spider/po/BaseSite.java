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
 * extended all references should be to Site
 */
public abstract class BaseSite extends BaseObject
{
    /** The Peer class */
    private static final SitePeer peer =
        new SitePeer();


    /** The value for the id field */
    private int id;

    /** The value for the website field */
    private String website;

    /** The value for the websitesuperurl field */
    private String websitesuperurl;

    /** The value for the middlepageurlreg field */
    private String middlepageurlreg;

    /** The value for the targetpageurlreg field */
    private String targetpageurlreg;

    /** The value for the frequency field */
    private String frequency;

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



        // update associated Objectattr
        if (collObjectattrs != null)
        {
            for (int i = 0; i < collObjectattrs.size(); i++)
            {
                ((Objectattr) collObjectattrs.get(i))
                        .setWebsite(v);
            }
        }

        // update associated Unvisitedurl
        if (collUnvisitedurls != null)
        {
            for (int i = 0; i < collUnvisitedurls.size(); i++)
            {
                ((Unvisitedurl) collUnvisitedurls.get(i))
                        .setWebsite(v);
            }
        }

        // update associated Visitedurl
        if (collVisitedurls != null)
        {
            for (int i = 0; i < collVisitedurls.size(); i++)
            {
                ((Visitedurl) collVisitedurls.get(i))
                        .setWebsite(v);
            }
        }
    }

    /**
     * Get the Websitesuperurl
     *
     * @return String
     */
    public String getWebsitesuperurl()
    {
        return websitesuperurl;
    }


    /**
     * Set the value of Websitesuperurl
     *
     * @param v new value
     */
    public void setWebsitesuperurl(String v) 
    {

        if (!ObjectUtils.equals(this.websitesuperurl, v))
        {
            this.websitesuperurl = v;
            setModified(true);
        }


    }

    /**
     * Get the Middlepageurlreg
     *
     * @return String
     */
    public String getMiddlepageurlreg()
    {
        return middlepageurlreg;
    }


    /**
     * Set the value of Middlepageurlreg
     *
     * @param v new value
     */
    public void setMiddlepageurlreg(String v) 
    {

        if (!ObjectUtils.equals(this.middlepageurlreg, v))
        {
            this.middlepageurlreg = v;
            setModified(true);
        }


    }

    /**
     * Get the Targetpageurlreg
     *
     * @return String
     */
    public String getTargetpageurlreg()
    {
        return targetpageurlreg;
    }


    /**
     * Set the value of Targetpageurlreg
     *
     * @param v new value
     */
    public void setTargetpageurlreg(String v) 
    {

        if (!ObjectUtils.equals(this.targetpageurlreg, v))
        {
            this.targetpageurlreg = v;
            setModified(true);
        }


    }

    /**
     * Get the Frequency
     *
     * @return String
     */
    public String getFrequency()
    {
        return frequency;
    }


    /**
     * Set the value of Frequency
     *
     * @param v new value
     */
    public void setFrequency(String v) 
    {

        if (!ObjectUtils.equals(this.frequency, v))
        {
            this.frequency = v;
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

       


    /**
     * Collection to store aggregation of collObjectattrs
     */
    protected List collObjectattrs;

    /**
     * Temporary storage of collObjectattrs to save a possible db hit in
     * the event objects are add to the collection, but the
     * complete collection is never requested.
     */
    protected void initObjectattrs()
    {
        if (collObjectattrs == null)
        {
            collObjectattrs = new ArrayList();
        }
    }


    /**
     * Method called to associate a Objectattr object to this object
     * through the Objectattr foreign key attribute
     *
     * @param l Objectattr
     * @throws TorqueException
     */
    public void addObjectattr(Objectattr l) throws TorqueException
    {
        getObjectattrs().add(l);
        l.setSite((Site) this);
    }

    /**
     * Method called to associate a Objectattr object to this object
     * through the Objectattr foreign key attribute using connection.
     *
     * @param l Objectattr
     * @throws TorqueException
     */
    public void addObjectattr(Objectattr l, Connection con) throws TorqueException
    {
        getObjectattrs(con).add(l);
        l.setSite((Site) this);
    }

    /**
     * The criteria used to select the current contents of collObjectattrs
     */
    private Criteria lastObjectattrsCriteria = null;

    /**
     * If this collection has already been initialized, returns
     * the collection. Otherwise returns the results of
     * getObjectattrs(new Criteria())
     *
     * @return the collection of associated objects
     * @throws TorqueException
     */
    public List getObjectattrs()
        throws TorqueException
    {
        if (collObjectattrs == null)
        {
            collObjectattrs = getObjectattrs(new Criteria(10));
        }
        return collObjectattrs;
    }

    /**
     * If this collection has already been initialized with
     * an identical criteria, it returns the collection.
     * Otherwise if this Site has previously
     * been saved, it will retrieve related Objectattrs from storage.
     * If this Site is new, it will return
     * an empty collection or the current collection, the criteria
     * is ignored on a new object.
     *
     * @throws TorqueException
     */
    public List getObjectattrs(Criteria criteria) throws TorqueException
    {
        if (collObjectattrs == null)
        {
            if (isNew())
            {
               collObjectattrs = new ArrayList();
            }
            else
            {
                criteria.add(ObjectattrPeer.WEBSITE, getWebsite() );
                collObjectattrs = ObjectattrPeer.doSelect(criteria);
            }
        }
        else
        {
            // criteria has no effect for a new object
            if (!isNew())
            {
                // the following code is to determine if a new query is
                // called for.  If the criteria is the same as the last
                // one, just return the collection.
                criteria.add(ObjectattrPeer.WEBSITE, getWebsite());
                if (!lastObjectattrsCriteria.equals(criteria))
                {
                    collObjectattrs = ObjectattrPeer.doSelect(criteria);
                }
            }
        }
        lastObjectattrsCriteria = criteria;

        return collObjectattrs;
    }

    /**
     * If this collection has already been initialized, returns
     * the collection. Otherwise returns the results of
     * getObjectattrs(new Criteria(),Connection)
     * This method takes in the Connection also as input so that
     * referenced objects can also be obtained using a Connection
     * that is taken as input
     */
    public List getObjectattrs(Connection con) throws TorqueException
    {
        if (collObjectattrs == null)
        {
            collObjectattrs = getObjectattrs(new Criteria(10), con);
        }
        return collObjectattrs;
    }

    /**
     * If this collection has already been initialized with
     * an identical criteria, it returns the collection.
     * Otherwise if this Site has previously
     * been saved, it will retrieve related Objectattrs from storage.
     * If this Site is new, it will return
     * an empty collection or the current collection, the criteria
     * is ignored on a new object.
     * This method takes in the Connection also as input so that
     * referenced objects can also be obtained using a Connection
     * that is taken as input
     */
    public List getObjectattrs(Criteria criteria, Connection con)
            throws TorqueException
    {
        if (collObjectattrs == null)
        {
            if (isNew())
            {
               collObjectattrs = new ArrayList();
            }
            else
            {
                 criteria.add(ObjectattrPeer.WEBSITE, getWebsite());
                 collObjectattrs = ObjectattrPeer.doSelect(criteria, con);
             }
         }
         else
         {
             // criteria has no effect for a new object
             if (!isNew())
             {
                 // the following code is to determine if a new query is
                 // called for.  If the criteria is the same as the last
                 // one, just return the collection.
                 criteria.add(ObjectattrPeer.WEBSITE, getWebsite());
                 if (!lastObjectattrsCriteria.equals(criteria))
                 {
                     collObjectattrs = ObjectattrPeer.doSelect(criteria, con);
                 }
             }
         }
         lastObjectattrsCriteria = criteria;

         return collObjectattrs;
     }











    /**
     * If this collection has already been initialized with
     * an identical criteria, it returns the collection.
     * Otherwise if this Site is new, it will return
     * an empty collection; or if this Site has previously
     * been saved, it will retrieve related Objectattrs from storage.
     *
     * This method is protected by default in order to keep the public
     * api reasonable.  You can provide public methods for those you
     * actually need in Site.
     */
    protected List getObjectattrsJoinSite(Criteria criteria)
        throws TorqueException
    {
        if (collObjectattrs == null)
        {
            if (isNew())
            {
               collObjectattrs = new ArrayList();
            }
            else
            {
                criteria.add(ObjectattrPeer.WEBSITE, getWebsite());
                collObjectattrs = ObjectattrPeer.doSelectJoinSite(criteria);
            }
        }
        else
        {
            // the following code is to determine if a new query is
            // called for.  If the criteria is the same as the last
            // one, just return the collection.
            criteria.add(ObjectattrPeer.WEBSITE, getWebsite());
            if (!lastObjectattrsCriteria.equals(criteria))
            {
                collObjectattrs = ObjectattrPeer.doSelectJoinSite(criteria);
            }
        }
        lastObjectattrsCriteria = criteria;

        return collObjectattrs;
    }





    /**
     * Collection to store aggregation of collUnvisitedurls
     */
    protected List collUnvisitedurls;

    /**
     * Temporary storage of collUnvisitedurls to save a possible db hit in
     * the event objects are add to the collection, but the
     * complete collection is never requested.
     */
    protected void initUnvisitedurls()
    {
        if (collUnvisitedurls == null)
        {
            collUnvisitedurls = new ArrayList();
        }
    }


    /**
     * Method called to associate a Unvisitedurl object to this object
     * through the Unvisitedurl foreign key attribute
     *
     * @param l Unvisitedurl
     * @throws TorqueException
     */
    public void addUnvisitedurl(Unvisitedurl l) throws TorqueException
    {
        getUnvisitedurls().add(l);
        l.setSite((Site) this);
    }

    /**
     * Method called to associate a Unvisitedurl object to this object
     * through the Unvisitedurl foreign key attribute using connection.
     *
     * @param l Unvisitedurl
     * @throws TorqueException
     */
    public void addUnvisitedurl(Unvisitedurl l, Connection con) throws TorqueException
    {
        getUnvisitedurls(con).add(l);
        l.setSite((Site) this);
    }

    /**
     * The criteria used to select the current contents of collUnvisitedurls
     */
    private Criteria lastUnvisitedurlsCriteria = null;

    /**
     * If this collection has already been initialized, returns
     * the collection. Otherwise returns the results of
     * getUnvisitedurls(new Criteria())
     *
     * @return the collection of associated objects
     * @throws TorqueException
     */
    public List getUnvisitedurls()
        throws TorqueException
    {
        if (collUnvisitedurls == null)
        {
            collUnvisitedurls = getUnvisitedurls(new Criteria(10));
        }
        return collUnvisitedurls;
    }

    /**
     * If this collection has already been initialized with
     * an identical criteria, it returns the collection.
     * Otherwise if this Site has previously
     * been saved, it will retrieve related Unvisitedurls from storage.
     * If this Site is new, it will return
     * an empty collection or the current collection, the criteria
     * is ignored on a new object.
     *
     * @throws TorqueException
     */
    public List getUnvisitedurls(Criteria criteria) throws TorqueException
    {
        if (collUnvisitedurls == null)
        {
            if (isNew())
            {
               collUnvisitedurls = new ArrayList();
            }
            else
            {
                criteria.add(UnvisitedurlPeer.WEBSITE, getWebsite() );
                collUnvisitedurls = UnvisitedurlPeer.doSelect(criteria);
            }
        }
        else
        {
            // criteria has no effect for a new object
            if (!isNew())
            {
                // the following code is to determine if a new query is
                // called for.  If the criteria is the same as the last
                // one, just return the collection.
                criteria.add(UnvisitedurlPeer.WEBSITE, getWebsite());
                if (!lastUnvisitedurlsCriteria.equals(criteria))
                {
                    collUnvisitedurls = UnvisitedurlPeer.doSelect(criteria);
                }
            }
        }
        lastUnvisitedurlsCriteria = criteria;

        return collUnvisitedurls;
    }

    /**
     * If this collection has already been initialized, returns
     * the collection. Otherwise returns the results of
     * getUnvisitedurls(new Criteria(),Connection)
     * This method takes in the Connection also as input so that
     * referenced objects can also be obtained using a Connection
     * that is taken as input
     */
    public List getUnvisitedurls(Connection con) throws TorqueException
    {
        if (collUnvisitedurls == null)
        {
            collUnvisitedurls = getUnvisitedurls(new Criteria(10), con);
        }
        return collUnvisitedurls;
    }

    /**
     * If this collection has already been initialized with
     * an identical criteria, it returns the collection.
     * Otherwise if this Site has previously
     * been saved, it will retrieve related Unvisitedurls from storage.
     * If this Site is new, it will return
     * an empty collection or the current collection, the criteria
     * is ignored on a new object.
     * This method takes in the Connection also as input so that
     * referenced objects can also be obtained using a Connection
     * that is taken as input
     */
    public List getUnvisitedurls(Criteria criteria, Connection con)
            throws TorqueException
    {
        if (collUnvisitedurls == null)
        {
            if (isNew())
            {
               collUnvisitedurls = new ArrayList();
            }
            else
            {
                 criteria.add(UnvisitedurlPeer.WEBSITE, getWebsite());
                 collUnvisitedurls = UnvisitedurlPeer.doSelect(criteria, con);
             }
         }
         else
         {
             // criteria has no effect for a new object
             if (!isNew())
             {
                 // the following code is to determine if a new query is
                 // called for.  If the criteria is the same as the last
                 // one, just return the collection.
                 criteria.add(UnvisitedurlPeer.WEBSITE, getWebsite());
                 if (!lastUnvisitedurlsCriteria.equals(criteria))
                 {
                     collUnvisitedurls = UnvisitedurlPeer.doSelect(criteria, con);
                 }
             }
         }
         lastUnvisitedurlsCriteria = criteria;

         return collUnvisitedurls;
     }











    /**
     * If this collection has already been initialized with
     * an identical criteria, it returns the collection.
     * Otherwise if this Site is new, it will return
     * an empty collection; or if this Site has previously
     * been saved, it will retrieve related Unvisitedurls from storage.
     *
     * This method is protected by default in order to keep the public
     * api reasonable.  You can provide public methods for those you
     * actually need in Site.
     */
    protected List getUnvisitedurlsJoinSite(Criteria criteria)
        throws TorqueException
    {
        if (collUnvisitedurls == null)
        {
            if (isNew())
            {
               collUnvisitedurls = new ArrayList();
            }
            else
            {
                criteria.add(UnvisitedurlPeer.WEBSITE, getWebsite());
                collUnvisitedurls = UnvisitedurlPeer.doSelectJoinSite(criteria);
            }
        }
        else
        {
            // the following code is to determine if a new query is
            // called for.  If the criteria is the same as the last
            // one, just return the collection.
            criteria.add(UnvisitedurlPeer.WEBSITE, getWebsite());
            if (!lastUnvisitedurlsCriteria.equals(criteria))
            {
                collUnvisitedurls = UnvisitedurlPeer.doSelectJoinSite(criteria);
            }
        }
        lastUnvisitedurlsCriteria = criteria;

        return collUnvisitedurls;
    }





    /**
     * Collection to store aggregation of collVisitedurls
     */
    protected List collVisitedurls;

    /**
     * Temporary storage of collVisitedurls to save a possible db hit in
     * the event objects are add to the collection, but the
     * complete collection is never requested.
     */
    protected void initVisitedurls()
    {
        if (collVisitedurls == null)
        {
            collVisitedurls = new ArrayList();
        }
    }


    /**
     * Method called to associate a Visitedurl object to this object
     * through the Visitedurl foreign key attribute
     *
     * @param l Visitedurl
     * @throws TorqueException
     */
    public void addVisitedurl(Visitedurl l) throws TorqueException
    {
        getVisitedurls().add(l);
        l.setSite((Site) this);
    }

    /**
     * Method called to associate a Visitedurl object to this object
     * through the Visitedurl foreign key attribute using connection.
     *
     * @param l Visitedurl
     * @throws TorqueException
     */
    public void addVisitedurl(Visitedurl l, Connection con) throws TorqueException
    {
        getVisitedurls(con).add(l);
        l.setSite((Site) this);
    }

    /**
     * The criteria used to select the current contents of collVisitedurls
     */
    private Criteria lastVisitedurlsCriteria = null;

    /**
     * If this collection has already been initialized, returns
     * the collection. Otherwise returns the results of
     * getVisitedurls(new Criteria())
     *
     * @return the collection of associated objects
     * @throws TorqueException
     */
    public List getVisitedurls()
        throws TorqueException
    {
        if (collVisitedurls == null)
        {
            collVisitedurls = getVisitedurls(new Criteria(10));
        }
        return collVisitedurls;
    }

    /**
     * If this collection has already been initialized with
     * an identical criteria, it returns the collection.
     * Otherwise if this Site has previously
     * been saved, it will retrieve related Visitedurls from storage.
     * If this Site is new, it will return
     * an empty collection or the current collection, the criteria
     * is ignored on a new object.
     *
     * @throws TorqueException
     */
    public List getVisitedurls(Criteria criteria) throws TorqueException
    {
        if (collVisitedurls == null)
        {
            if (isNew())
            {
               collVisitedurls = new ArrayList();
            }
            else
            {
                criteria.add(VisitedurlPeer.WEBSITE, getWebsite() );
                collVisitedurls = VisitedurlPeer.doSelect(criteria);
            }
        }
        else
        {
            // criteria has no effect for a new object
            if (!isNew())
            {
                // the following code is to determine if a new query is
                // called for.  If the criteria is the same as the last
                // one, just return the collection.
                criteria.add(VisitedurlPeer.WEBSITE, getWebsite());
                if (!lastVisitedurlsCriteria.equals(criteria))
                {
                    collVisitedurls = VisitedurlPeer.doSelect(criteria);
                }
            }
        }
        lastVisitedurlsCriteria = criteria;

        return collVisitedurls;
    }

    /**
     * If this collection has already been initialized, returns
     * the collection. Otherwise returns the results of
     * getVisitedurls(new Criteria(),Connection)
     * This method takes in the Connection also as input so that
     * referenced objects can also be obtained using a Connection
     * that is taken as input
     */
    public List getVisitedurls(Connection con) throws TorqueException
    {
        if (collVisitedurls == null)
        {
            collVisitedurls = getVisitedurls(new Criteria(10), con);
        }
        return collVisitedurls;
    }

    /**
     * If this collection has already been initialized with
     * an identical criteria, it returns the collection.
     * Otherwise if this Site has previously
     * been saved, it will retrieve related Visitedurls from storage.
     * If this Site is new, it will return
     * an empty collection or the current collection, the criteria
     * is ignored on a new object.
     * This method takes in the Connection also as input so that
     * referenced objects can also be obtained using a Connection
     * that is taken as input
     */
    public List getVisitedurls(Criteria criteria, Connection con)
            throws TorqueException
    {
        if (collVisitedurls == null)
        {
            if (isNew())
            {
               collVisitedurls = new ArrayList();
            }
            else
            {
                 criteria.add(VisitedurlPeer.WEBSITE, getWebsite());
                 collVisitedurls = VisitedurlPeer.doSelect(criteria, con);
             }
         }
         else
         {
             // criteria has no effect for a new object
             if (!isNew())
             {
                 // the following code is to determine if a new query is
                 // called for.  If the criteria is the same as the last
                 // one, just return the collection.
                 criteria.add(VisitedurlPeer.WEBSITE, getWebsite());
                 if (!lastVisitedurlsCriteria.equals(criteria))
                 {
                     collVisitedurls = VisitedurlPeer.doSelect(criteria, con);
                 }
             }
         }
         lastVisitedurlsCriteria = criteria;

         return collVisitedurls;
     }











    /**
     * If this collection has already been initialized with
     * an identical criteria, it returns the collection.
     * Otherwise if this Site is new, it will return
     * an empty collection; or if this Site has previously
     * been saved, it will retrieve related Visitedurls from storage.
     *
     * This method is protected by default in order to keep the public
     * api reasonable.  You can provide public methods for those you
     * actually need in Site.
     */
    protected List getVisitedurlsJoinSite(Criteria criteria)
        throws TorqueException
    {
        if (collVisitedurls == null)
        {
            if (isNew())
            {
               collVisitedurls = new ArrayList();
            }
            else
            {
                criteria.add(VisitedurlPeer.WEBSITE, getWebsite());
                collVisitedurls = VisitedurlPeer.doSelectJoinSite(criteria);
            }
        }
        else
        {
            // the following code is to determine if a new query is
            // called for.  If the criteria is the same as the last
            // one, just return the collection.
            criteria.add(VisitedurlPeer.WEBSITE, getWebsite());
            if (!lastVisitedurlsCriteria.equals(criteria))
            {
                collVisitedurls = VisitedurlPeer.doSelectJoinSite(criteria);
            }
        }
        lastVisitedurlsCriteria = criteria;

        return collVisitedurls;
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
            fieldNames.add("Websitesuperurl");
            fieldNames.add("Middlepageurlreg");
            fieldNames.add("Targetpageurlreg");
            fieldNames.add("Frequency");
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
        if (name.equals("Websitesuperurl"))
        {
            return getWebsitesuperurl();
        }
        if (name.equals("Middlepageurlreg"))
        {
            return getMiddlepageurlreg();
        }
        if (name.equals("Targetpageurlreg"))
        {
            return getTargetpageurlreg();
        }
        if (name.equals("Frequency"))
        {
            return getFrequency();
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
        if (name.equals("Websitesuperurl"))
        {
            // Object fields can be null
            if (value != null && ! String.class.isInstance(value))
            {
                throw new IllegalArgumentException("Invalid type of object specified for value in setByName");
            }
            setWebsitesuperurl((String) value);
            return true;
        }
        if (name.equals("Middlepageurlreg"))
        {
            // Object fields can be null
            if (value != null && ! String.class.isInstance(value))
            {
                throw new IllegalArgumentException("Invalid type of object specified for value in setByName");
            }
            setMiddlepageurlreg((String) value);
            return true;
        }
        if (name.equals("Targetpageurlreg"))
        {
            // Object fields can be null
            if (value != null && ! String.class.isInstance(value))
            {
                throw new IllegalArgumentException("Invalid type of object specified for value in setByName");
            }
            setTargetpageurlreg((String) value);
            return true;
        }
        if (name.equals("Frequency"))
        {
            // Object fields can be null
            if (value != null && ! String.class.isInstance(value))
            {
                throw new IllegalArgumentException("Invalid type of object specified for value in setByName");
            }
            setFrequency((String) value);
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
        if (name.equals(SitePeer.ID))
        {
            return new Integer(getId());
        }
        if (name.equals(SitePeer.WEBSITE))
        {
            return getWebsite();
        }
        if (name.equals(SitePeer.WEBSITESUPERURL))
        {
            return getWebsitesuperurl();
        }
        if (name.equals(SitePeer.MIDDLEPAGEURLREG))
        {
            return getMiddlepageurlreg();
        }
        if (name.equals(SitePeer.TARGETPAGEURLREG))
        {
            return getTargetpageurlreg();
        }
        if (name.equals(SitePeer.FREQUENCY))
        {
            return getFrequency();
        }
        if (name.equals(SitePeer.CREATETIME))
        {
            return getCreatetime();
        }
        if (name.equals(SitePeer.UPDATETIME))
        {
            return getUpdatetime();
        }
        if (name.equals(SitePeer.OPERATOR))
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
      if (SitePeer.ID.equals(name))
        {
            return setByName("Id", value);
        }
      if (SitePeer.WEBSITE.equals(name))
        {
            return setByName("Website", value);
        }
      if (SitePeer.WEBSITESUPERURL.equals(name))
        {
            return setByName("Websitesuperurl", value);
        }
      if (SitePeer.MIDDLEPAGEURLREG.equals(name))
        {
            return setByName("Middlepageurlreg", value);
        }
      if (SitePeer.TARGETPAGEURLREG.equals(name))
        {
            return setByName("Targetpageurlreg", value);
        }
      if (SitePeer.FREQUENCY.equals(name))
        {
            return setByName("Frequency", value);
        }
      if (SitePeer.CREATETIME.equals(name))
        {
            return setByName("Createtime", value);
        }
      if (SitePeer.UPDATETIME.equals(name))
        {
            return setByName("Updatetime", value);
        }
      if (SitePeer.OPERATOR.equals(name))
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
            return getWebsitesuperurl();
        }
        if (pos == 3)
        {
            return getMiddlepageurlreg();
        }
        if (pos == 4)
        {
            return getTargetpageurlreg();
        }
        if (pos == 5)
        {
            return getFrequency();
        }
        if (pos == 6)
        {
            return getCreatetime();
        }
        if (pos == 7)
        {
            return getUpdatetime();
        }
        if (pos == 8)
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
            return setByName("Websitesuperurl", value);
        }
    if (position == 3)
        {
            return setByName("Middlepageurlreg", value);
        }
    if (position == 4)
        {
            return setByName("Targetpageurlreg", value);
        }
    if (position == 5)
        {
            return setByName("Frequency", value);
        }
    if (position == 6)
        {
            return setByName("Createtime", value);
        }
    if (position == 7)
        {
            return setByName("Updatetime", value);
        }
    if (position == 8)
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
        save(SitePeer.DATABASE_NAME);
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
                    SitePeer.doInsert((Site) this, con);
                    setNew(false);
                }
                else
                {
                    SitePeer.doUpdate((Site) this, con);
                }
            }


            if (collObjectattrs != null)
            {
                for (int i = 0; i < collObjectattrs.size(); i++)
                {
                    ((Objectattr) collObjectattrs.get(i)).save(con);
                }
            }

            if (collUnvisitedurls != null)
            {
                for (int i = 0; i < collUnvisitedurls.size(); i++)
                {
                    ((Unvisitedurl) collUnvisitedurls.get(i)).save(con);
                }
            }

            if (collVisitedurls != null)
            {
                for (int i = 0; i < collVisitedurls.size(); i++)
                {
                    ((Visitedurl) collVisitedurls.get(i)).save(con);
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
    public Site copy() throws TorqueException
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
    public Site copy(Connection con) throws TorqueException
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
    public Site copy(boolean deepcopy) throws TorqueException
    {
        return copyInto(new Site(), deepcopy);
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
    public Site copy(boolean deepcopy, Connection con) throws TorqueException
    {
        return copyInto(new Site(), deepcopy, con);
    }
  
    /**
     * Fills the copyObj with the contents of this object.
     * The associated objects are also copied and treated as new objects.
     *
     * @param copyObj the object to fill.
     */
    protected Site copyInto(Site copyObj) throws TorqueException
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
    protected Site copyInto(Site copyObj, Connection con) throws TorqueException
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
    protected Site copyInto(Site copyObj, boolean deepcopy) throws TorqueException
    {
        copyObj.setId(id);
        copyObj.setWebsite(website);
        copyObj.setWebsitesuperurl(websitesuperurl);
        copyObj.setMiddlepageurlreg(middlepageurlreg);
        copyObj.setTargetpageurlreg(targetpageurlreg);
        copyObj.setFrequency(frequency);
        copyObj.setCreatetime(createtime);
        copyObj.setUpdatetime(updatetime);
        copyObj.setOperator(operator);

        copyObj.setId( 0);

        if (deepcopy)
        {


        List vObjectattrs = getObjectattrs();
        if (vObjectattrs != null)
        {
            for (int i = 0; i < vObjectattrs.size(); i++)
            {
                Objectattr obj = (Objectattr) vObjectattrs.get(i);
                copyObj.addObjectattr(obj.copy());
            }
        }
        else
        {
            copyObj.collObjectattrs = null;
        }


        List vUnvisitedurls = getUnvisitedurls();
        if (vUnvisitedurls != null)
        {
            for (int i = 0; i < vUnvisitedurls.size(); i++)
            {
                Unvisitedurl obj = (Unvisitedurl) vUnvisitedurls.get(i);
                copyObj.addUnvisitedurl(obj.copy());
            }
        }
        else
        {
            copyObj.collUnvisitedurls = null;
        }


        List vVisitedurls = getVisitedurls();
        if (vVisitedurls != null)
        {
            for (int i = 0; i < vVisitedurls.size(); i++)
            {
                Visitedurl obj = (Visitedurl) vVisitedurls.get(i);
                copyObj.addVisitedurl(obj.copy());
            }
        }
        else
        {
            copyObj.collVisitedurls = null;
        }
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
    protected Site copyInto(Site copyObj, boolean deepcopy, Connection con) throws TorqueException
    {
        copyObj.setId(id);
        copyObj.setWebsite(website);
        copyObj.setWebsitesuperurl(websitesuperurl);
        copyObj.setMiddlepageurlreg(middlepageurlreg);
        copyObj.setTargetpageurlreg(targetpageurlreg);
        copyObj.setFrequency(frequency);
        copyObj.setCreatetime(createtime);
        copyObj.setUpdatetime(updatetime);
        copyObj.setOperator(operator);

        copyObj.setId( 0);

        if (deepcopy)
        {


        List vObjectattrs = getObjectattrs(con);
        if (vObjectattrs != null)
        {
            for (int i = 0; i < vObjectattrs.size(); i++)
            {
                Objectattr obj = (Objectattr) vObjectattrs.get(i);
                copyObj.addObjectattr(obj.copy(con), con);
            }
        }
        else
        {
            copyObj.collObjectattrs = null;
        }


        List vUnvisitedurls = getUnvisitedurls(con);
        if (vUnvisitedurls != null)
        {
            for (int i = 0; i < vUnvisitedurls.size(); i++)
            {
                Unvisitedurl obj = (Unvisitedurl) vUnvisitedurls.get(i);
                copyObj.addUnvisitedurl(obj.copy(con), con);
            }
        }
        else
        {
            copyObj.collUnvisitedurls = null;
        }


        List vVisitedurls = getVisitedurls(con);
        if (vVisitedurls != null)
        {
            for (int i = 0; i < vVisitedurls.size(); i++)
            {
                Visitedurl obj = (Visitedurl) vVisitedurls.get(i);
                copyObj.addVisitedurl(obj.copy(con), con);
            }
        }
        else
        {
            copyObj.collVisitedurls = null;
        }
        }
        return copyObj;
    }
    
    

    /**
     * returns a peer instance associated with this om.  Since Peer classes
     * are not to have any instance attributes, this method returns the
     * same instance for all member of this class. The method could therefore
     * be static, but this would prevent one from overriding the behavior.
     */
    public SitePeer getPeer()
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
        return SitePeer.getTableMap();
    }


    public String toString()
    {
        StringBuffer str = new StringBuffer();
        str.append("Site:\n");
        str.append("Id = ")
           .append(getId())
           .append("\n");
        str.append("Website = ")
           .append(getWebsite())
           .append("\n");
        str.append("Websitesuperurl = ")
           .append(getWebsitesuperurl())
           .append("\n");
        str.append("Middlepageurlreg = ")
           .append(getMiddlepageurlreg())
           .append("\n");
        str.append("Targetpageurlreg = ")
           .append(getTargetpageurlreg())
           .append("\n");
        str.append("Frequency = ")
           .append(getFrequency())
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
