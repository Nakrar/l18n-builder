# Css challenge

In this exercise we're implementing CSS to make given HTML look like given design (original design not included). 

### Changes to original HTML

* changed icons `src`
* added `<head>`
* image has been swapped and data-tags removed, just in case

### Known issues:

* Using tab, upload button would be focused 2 times.
    First, container would receive focus. Then button itself. 
    Being allowed modify original HTML, we could set `tabindex="0"` for `button` and `input`. 
* Icon colorization has been done with `filter`. We could use `fill` and `<svg>` instead. It would allow us to set the exact color.
* File `<input>` is hidden for now. 
