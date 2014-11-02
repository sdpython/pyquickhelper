It is sometimes difficult to navigate through long notebooks. Regular
ways to navigate in a HTML page are not available when the cursor is
stuck in a cell. Here is a simple trick with two sections. Links remains
at the same place anytime just by adding HTML in the notebook.

.. raw:: html

   <div
   style="position:absolute; top:10px; right:5px; width:100px; height:90px; margin:10px;">

`Section 1 <#section1>`__ -- `Section 2 <#section2>`__ -- `This is the
end <#end>`__

.. raw:: html

   </div>

The code in the markdown cell looks like the following, it is a mix
between HTML and markdown. The combination is not perfect but that works
somehow. The outcome can be shown on the left.
