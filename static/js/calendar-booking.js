/* BOOKING DATA VARIABLES */

let dateBookings = {};
let currentDate = new Date();
let selectedDate = null;
let selectedTime = null;

/* CONFIGURATION */

const timeSlots = [
    { value: '14:00', label: '2:00 PM' },
    { value: '16:00', label: '4:00 PM' },
    { value: '18:00', label: '6:00 PM' },
    { value: '20:00', label: '8:00 PM' }
];

const monthNames = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
];

const dayNames = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

/* DOM ELEMENT REFERENCES */

const bookedSlotsData = document.getElementById('booked-slots-data');
const prevMonthBtn = document.getElementById('prevMonth');
const nextMonthBtn = document.getElementById('nextMonth');
const currentMonthEl = document.getElementById('currentMonth');
const calendarGrid = document.getElementById('calendarGrid');
const selectedDateTitle = document.getElementById('selectedDateTitle');
const timeSlotsList = document.getElementById('timeSlotsList');
const timeSlotsSection = document.getElementById('timeSlotsSection');
const selectDatePrompt = document.getElementById('selectDatePrompt');
const bookingFormSection = document.getElementById('bookingFormSection');
const confirmDateTime = document.getElementById('confirmDateTime');
const formDate = document.getElementById('formDate');
const formTime = document.getElementById('formTime');

/* DATA PROCESSING */

/**
 * Processes booked slots data and organizes by date
 * @param {Array} bookedSlots - Array of booking objects with date and time
 * @returns {Object} - Object with dates as keys and arrays of booked times as values
 */
function processBookedSlots(bookedSlots) {
    const bookings = {};
    
    bookedSlots.forEach(slot => {
        if (!bookings[slot.date]) {
            bookings[slot.date] = [];
        }
        bookings[slot.date].push(slot.time);
    });
    
    return bookings;
}

/* CALENDAR RENDERING */

/**
 * Renders the calendar for the current month
 * Displays days with availability indicators and handles past dates
 */
function renderCalendar() {
    const year = currentDate.getFullYear();
    const month = currentDate.getMonth();
    
    // Update month display
    currentMonthEl.textContent = `${monthNames[month]} ${year}`;
    
    // Get calendar info
    const firstDay = new Date(year, month, 1).getDay();
    const daysInMonth = new Date(year, month + 1, 0).getDate();
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    
    // Build calendar HTML
    let html = '';
    
    // Day headers
    dayNames.forEach(day => {
        html += `<div class="calendar-header">${day}</div>`;
    });
    
    // Empty cells before month starts
    for (let i = 0; i < firstDay; i++) {
        html += '<div class="calendar-day disabled"></div>';
    }
    
    // Days of month
    for (let day = 1; day <= daysInMonth; day++) {
        const dateStr = formatDateString(year, month, day);
        const date = new Date(year, month, day);
        
        const classes = getDateClasses(date, dateStr, today);
        
        html += `<div class="${classes.join(' ')}" data-date="${dateStr}">${day}</div>`;
    }
    
    calendarGrid.innerHTML = html;
    
    // Add click handlers to available dates
    attachDateClickHandlers();
}

/**
 * Formats a date into YYYY-MM-DD string format
 * @param {number} year - The year
 * @param {number} month - The month (0-11)
 * @param {number} day - The day of month
 * @returns {string} - Formatted date string
 */
function formatDateString(year, month, day) {
    return `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
}

/**
 * Determines CSS classes for a calendar date based on its status
 * @param {Date} date - The date object
 * @param {string} dateStr - The formatted date string
 * @param {Date} today - Today's date
 * @returns {Array} - Array of CSS class names
 */
function getDateClasses(date, dateStr, today) {
    const classes = ['calendar-day'];
    
    // Check if past
    if (date < today) {
        classes.push('past');
    } else {
        // Check availability
        const booked = dateBookings[dateStr] || [];
        if (booked.length === 0) {
            classes.push('available');
        } else if (booked.length >= timeSlots.length) {
            classes.push('full');
        } else {
            classes.push('limited');
        }
    }
    
    // Check if today
    if (date.toDateString() === today.toDateString()) {
        classes.push('today');
    }
    
    // Check if selected
    if (selectedDate === dateStr) {
        classes.push('selected');
    }
    
    return classes;
}

/**
 * Attaches click event handlers to all available calendar dates
 */
function attachDateClickHandlers() {
    document.querySelectorAll('.calendar-day:not(.past):not(.disabled)').forEach(dayEl => {
        dayEl.addEventListener('click', function() {
            selectDate(this.dataset.date);
        });
    });
}

/* DATE SELECTION */

/**
 * Handles date selection and updates the UI
 * @param {string} dateStr - The selected date in YYYY-MM-DD format
 */
function selectDate(dateStr) {
    selectedDate = dateStr;
    selectedTime = null;
    
    // Update calendar display
    document.querySelectorAll('.calendar-day').forEach(el => el.classList.remove('selected'));
    document.querySelector(`[data-date="${dateStr}"]`).classList.add('selected');
    
    // Show time slots
    showTimeSlots(dateStr);
}

/* TIME SLOT DISPLAY */

/**
 * Displays available time slots for the selected date
 * @param {string} dateStr - The selected date in YYYY-MM-DD format
 */
function showTimeSlots(dateStr) {
    const booked = dateBookings[dateStr] || [];
    const date = new Date(dateStr + 'T00:00:00');
    const dateDisplay = date.toLocaleDateString('en-US', { 
        weekday: 'long', 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric' 
    });
    
    selectedDateTitle.textContent = dateDisplay;
    
    // Build time slots HTML
    let html = '';
    timeSlots.forEach(slot => {
        const isBooked = booked.includes(slot.value);
        const classes = ['time-slot'];
        if (isBooked) classes.push('booked');
        
        html += `
            <div class="${classes.join(' ')}" data-time="${slot.value}" ${isBooked ? 'disabled' : ''}>
                ${slot.label}
                ${isBooked ? '<br><small>Booked</small>' : ''}
            </div>
        `;
    });
    
    timeSlotsList.innerHTML = html;
    
    // Show time slots section, hide prompt
    timeSlotsSection.style.display = 'block';
    selectDatePrompt.style.display = 'none';
    bookingFormSection.style.display = 'none';
    
    // Add click handlers to available time slots
    attachTimeSlotClickHandlers();
}

/**
 * Attaches click event handlers to all available time slots
 */
function attachTimeSlotClickHandlers() {
    document.querySelectorAll('.time-slot:not(.booked)').forEach(slotEl => {
        slotEl.addEventListener('click', function() {
            selectTime(this.dataset.time);
        });
    });
}

/* TIME SELECTION */

/**
 * Handles time slot selection and updates the UI
 * @param {string} time - The selected time in HH:MM format
 */
function selectTime(time) {
    selectedTime = time;
    
    // Update time slot display
    document.querySelectorAll('.time-slot').forEach(el => el.classList.remove('selected'));
    document.querySelector(`[data-time="${time}"]`).classList.add('selected');
    
    // Show booking form
    showBookingForm();
}

/* BOOKING FORM */

/**
 * Displays the booking form with selected date and time
 * Populates hidden form fields and scrolls to form
 */
function showBookingForm() {
    const date = new Date(selectedDate + 'T00:00:00');
    const dateDisplay = date.toLocaleDateString('en-US', { 
        weekday: 'long', 
        month: 'long', 
        day: 'numeric',
        year: 'numeric'
    });
    const timeDisplay = timeSlots.find(t => t.value === selectedTime).label;
    
    // Update confirmation text
    confirmDateTime.textContent = `${dateDisplay} at ${timeDisplay}`;
    
    // Set hidden form fields
    formDate.value = selectedDate;
    formTime.value = selectedTime;
    
    // Show form
    bookingFormSection.style.display = 'block';
    
    // Scroll to form
    bookingFormSection.scrollIntoView({ 
        behavior: 'smooth', 
        block: 'start' 
    });
}

/* NAVIGATION */

/**
 * Navigates to the previous month
 */
function navigatePreviousMonth() {
    currentDate.setMonth(currentDate.getMonth() - 1);
    renderCalendar();
}

/**
 * Navigates to the next month
 */
function navigateNextMonth() {
    currentDate.setMonth(currentDate.getMonth() + 1);
    renderCalendar();
}

/* EVENT LISTENERS */

// Month navigation
prevMonthBtn.addEventListener('click', navigatePreviousMonth);
nextMonthBtn.addEventListener('click', navigateNextMonth);

/* INITIALIZATION */

/**
 * Initializes the calendar booking system
 * Loads booked slots and renders the initial calendar
 */
function initializeCalendar() {
    // Load and process booked slots data
    const bookedSlots = JSON.parse(bookedSlotsData.textContent);
    dateBookings = processBookedSlots(bookedSlots);
    
    // Render initial calendar
    renderCalendar();
}

// Initialize the calendar when the page loads
document.addEventListener('DOMContentLoaded', initializeCalendar);