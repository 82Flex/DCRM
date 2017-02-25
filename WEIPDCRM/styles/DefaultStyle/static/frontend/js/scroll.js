/**
 * 
 * Find more about the scrolling function at
 * http://cubiq.org/scrolling-div-on-iphone-ipod-touch/5
 *
 * Copyright (c) 2009 Matteo Spinelli, http://cubiq.org/
 * Released under MIT license
 * http://cubiq.org/dropbox/mit-license.txt
 * 
 * Version 2.3 - Last updated: 2009.07.09
 * Modified to support horizontal scroll by phoenix3200 and rpetrich
 * 
 */
 
function iScroll(wrapper)
{
	window.setTimeout(function(t) { t.init(wrapper); }, 100, this);
}

iScroll.prototype = {
	init: function(wrapper) {
		if (typeof(window.orientation) == "number") {
			this.wrapper = wrapper;
			this.element = wrapper.children[0];
			this.lastIndex = this.element.children.length-1;
			var pipsElement = wrapper.children[1];
			if (pipsElement)
			{
				for (var i=0; i<this.element.children.length; i++) {
					var pip = document.createElement("span");
					pip.className = "pip";
					pip.innerHTML = "&bull;"
					pipsElement.appendChild(pip);
				}
				this.pips = pipsElement.children;
			}
			this._idx = 0;
			this.idx = 0;

			this.refreshPadding();

			this.position = 0;
			this.vertical = 0;
			this.refresh();
			this.element.style.webkitTransitionTimingFunction = 'cubic-bezier(0, 0, 0.2, 1)';
			this.acceleration = 0.009;

			wrapper.style.overflowX = 'hidden';

			wrapper.addEventListener('touchstart', this, true);
			window.addEventListener('orientationchange', this, true);
		}
	},

	handleEvent: function(e) {
		switch(e.type) {
			case 'touchstart': this.onTouchStart(e); break;
			case 'touchmove': this.onTouchMove(e); break;
			case 'touchend': this.onTouchEnd(e); break;
			case 'webkitTransitionEnd': this.onTransitionEnd(e); break;
			case 'orientationchange': this.onOrientationChange(e); break;
		}
	},

	get position() {
		return this._position;
	},

	set position(pos) {
		this._position = pos;
		this.element.style.webkitTransform = 'translate3d(' + this._position + 'px, 0, 0)';
	},

	get idx()
	{
		return this._idx;
	},

	set idx(idx)
	{
		if (this.pips) {
			this.pips[this._idx].className = "pip";
			this.pips[idx].className = "selected pip";
		}
		this._idx = idx;
	},

	refreshPadding: function() {
		this.wrapper.style.webkitTransform = 'translate3d(0,0,0)';
		var cw = this.wrapper.clientWidth;
		var fc = this.element.children[0];
		this.element.style.width = ((this.lastIndex + 1) * (fc.clientWidth + 15)) + (cw - fc.clientWidth) + 'px';
		this.element.style.paddingLeft = ((cw - fc.clientWidth - 30) / 2) + 'px';
	},

	refresh: function() {
		this.element.style.webkitTransitionDuration = '0';

		if( this.element.offsetWidth<this.wrapper.clientWidth )
			this.maxScroll = 0;
		else
			this.maxScroll = this.wrapper.clientWidth - this.element.offsetWidth;
	},

	onOrientationChange: function(e) {
		this.refreshPadding();
		this.refresh();
		window.setTimeout(function(t) { t.refreshPadding(); t.refresh(); }, 100, this);
	},

	onTouchStart: function(e) {
		this.element.style.webkitTransitionDuration = '0';	// Remove any transition
		var theTransform = window.getComputedStyle(this.element).webkitTransform;
		theTransform = new WebKitCSSMatrix(theTransform).m41;
		if (theTransform!=this.position)
			this.position = theTransform;

		this.startX = e.targetTouches[0].clientX;
		this.startY = e.targetTouches[0].clientY;
		this.firstMove = true;
		this.scrollStartX = this.position;
		this.scrollStartTime = e.timeStamp;
		this.moved = false;

		this.wrapper.addEventListener('touchmove', this, true);
		this.wrapper.addEventListener('touchend', this, true);

		return false;
	},
	
	onTouchMove: function(e) {
		if (this.firstMove) {
			this.firstMove = false;
			this.inMove = Math.abs(e.targetTouches[0].clientX - this.startX) > Math.abs(e.targetTouches[0].clientY - this.startY);
			if (this.inMove)
				this.wrapper.scrollIntoView();
		}
		if (!this.inMove)
			return false;
		e.preventDefault();
		if (e.targetTouches.length != 1)
			return false;

		var leftDelta = e.targetTouches[0].clientX - this.startX;
		if (this.position>0 || this.position<this.maxScroll)
			leftDelta/=2;
		this.position = this.position + leftDelta;
		this.startX = e.targetTouches[0].clientX;
		this.moved = true;

		// Prevent slingshot effect
		if (e.timeStamp-this.scrollStartTime>100) {
			this.scrollStartX = this.position;
			this.scrollStartTime = e.timeStamp;
		}

		return false;
	},
	
	onTouchEnd: function(e) {
		this.wrapper.removeEventListener('touchmove', this, false);
		this.wrapper.removeEventListener('touchend', this, false);

		// If we are outside of the boundaries, let's go back to the sheepfold
		if( this.position>0 || this.position<this.maxScroll ) {
			this.element.style.webkitTransitionTimingFunction = 'cubic-bezier(0, 0, 0.2, 1)';
			if (this.position > 0) {
				this.scrollTo(0);
				this.idx = 0;
			} else {
				this.scrollTo(this.maxScroll);
				this.idx = this.lastIndex;
			}
			return false;
		}


		// Lame formula to calculate a fake deceleration
		var scrollDistance = this.position - this.scrollStartX;
		var scrollDuration = e.timeStamp - this.scrollStartTime;

		var newDuration = (2 * scrollDistance / scrollDuration) / this.acceleration;
		var newScrollDistance = (this.acceleration / 2) * (newDuration * newDuration);

		if( newDuration<0 ) {
			newDuration = -newDuration;
			newScrollDistance = -newScrollDistance;
		}

		var speed = scrollDistance / scrollDuration;
		if(speed < 0)
			speed = -speed;

		var ict = this.lastIndex;

		this.idx = Math.round(this.position * ict / this.maxScroll);
		var newPosition = this.maxScroll/ict * this.idx;
		if(speed > 0.3) {
			if (this.position - newPosition < 0 && scrollDistance < 0)
				this.idx = this.idx + 1;
			else if (this.position - newPosition > 0 && scrollDistance > 0)
				this.idx = this.idx - 1;
			newPosition = this.maxScroll/ict * this.idx;

			var newScrollDistance = newPosition - this.position;
			if(newScrollDistance < 0)
				newScrollDistance = -newScrollDistance;

			if(speed < 0.7)
				newScrollDistance = newScrollDistance * speed /50;
			else
				newScrollDistance = newScrollDistance / 500;

			this.element.style.webkitTransitionTimingFunction = 'cubic-bezier(0, 0, 0.2, 1)';
			this.scrollTo(newPosition, newScrollDistance + 's'); 
			return false;
		} else {
			var newScrollDistance = newPosition - this.position;
			if(newScrollDistance < 0)
				newScrollDistance = -newScrollDistance;
			newScrollDistance = newScrollDistance * 5;
			
			this.element.style.webkitTransitionTimingFunction = 'cubic-bezier(0, 0, 0.2, 1)';
			this.scrollTo(newPosition, newScrollDistance + 'ms');
			return false;
		}

		/*var newPosition = this.position + newScrollDistance;
		
		if (newPosition>this.wrapper.clientWidth/2)
			newPosition = this.wrapper.clientWidth/2;
		else if (newPosition>0)
			newPosition/= 1.5;
		else if (newPosition<this.maxScroll-this.wrapper.clientWidth/2)
			newPosition = this.maxScroll-this.wrapper.clientWidth/2;
		else if (newPosition<this.maxScroll)
			newPosition = (newPosition - this.maxScroll) / 1.5 + this.maxScroll;
		else
			newDuration *= 6;

		this.element.style.webkitTransitionTimingFunction = 'cubic-bezier(0, 0, 0.2, 1)';
		this.scrollTo(newPosition, Math.round(newDuration) + 'ms');

		return false;*/
	},

	onTransitionEnd: function() {
		this.wrapper.removeEventListener('webkitTransitionEnd', this, false);
		this.element.style.webkitTransitionTimingFunction = 'cubic-bezier(1, 0.2, 0.2, 1)';
		this.scrollTo( this.position>0 ? 0 : this.maxScroll );
	},

	scrollTo: function(dest, runtime) {
		this.element.style.webkitTransitionDuration = runtime ? runtime : '300ms';
		this.position = dest ? dest : 0;

		// If we are outside of the boundaries at the end of the transition go back to the sheepfold
		if( this.position>0 || this.position<this.maxScroll )
			this.wrapper.addEventListener('webkitTransitionEnd', this, true);
	}
};