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

function renderCalendar() {
    const year = currentDate.getFullYear();
    const month = currentDate.getMonth();
    
    currentMonthEl.textContent = `${monthNames[month]} ${year}`;
    
    const firstDay = new Date(year, month, 1).getDay();
    const daysInMonth = new Date(year, month + 1, 0).getDate();
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    
    let html = '';
    
    dayNames.forEach(day => {
        html += `<div class="calendar-header">${day}</div>`;
    });
    
    for (let i = 0; i < firstDay; i++) {
        html += '<div class="calendar-day disabled"></div>';
    }
    
    for (let day = 1; day <= daysInMonth; day++) {
        const dateStr = formatDateString(year, month, day);
        const date = new Date(year, month, day);
        
        const classes = getDateClasses(date, dateStr, today);
        
        html += `<div class="${classes.join(' ')}" data-date="${dateStr}">${day}</div>`;
    }
    
    calendarGrid.innerHTML = html;
    attachDateClickHandlers();
}

function formatDateString(year, month, day) {
    return `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
}

function getDateClasses(date, dateStr, today) {
    const classes = ['calendar-day'];
    
    if (date < today) {
        classes.push('past');
    } else {
        const booked = dateBookings[dateStr] || [];
        if (booked.length === 0) {
            classes.push('available');
        } else if (booked.length >= timeSlots.length) {
            classes.push('full');
        } else {
            classes.push('limited');
        }
    }
    
    if (date.toDateString() === today.toDateString()) {
        classes.push('today');
    }
    
    if (selectedDate === dateStr) {
        classes.push('selected');
    }
    
    return classes;
}

function attachDateClickHandlers() {
    document.querySelectorAll('.calendar-day:not(.past):not(.disabled)').forEach(dayEl => {
        dayEl.addEventListener('click', function() {
            selectDate(this.dataset.date);
        });
    });
}

/* DATE SELECTION */

function selectDate(dateStr) {
    selectedDate = dateStr;
    selectedTime = null;
    
    document.querySelectorAll('.calendar-day').forEach(el => el.classList.remove('selected'));
    document.querySelector(`[data-date="${dateStr}"]`).classList.add('selected');
    
    showTimeSlots(dateStr);
}

/* TIME SLOT DISPLAY */

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
    
    timeSlotsSection.style.display = 'block';
    selectDatePrompt.style.display = 'none';
    bookingFormSection.style.display = 'none';
    
    attachTimeSlotClickHandlers();
}

function attachTimeSlotClickHandlers() {
    document.querySelectorAll('.time-slot:not(.booked)').forEach(slotEl => {
        slotEl.addEventListener('click', function() {
            selectTime(this.dataset.time);
        });
    });
}

/* TIME SELECTION */

function selectTime(time) {
    selectedTime = time;
    
    document.querySelectorAll('.time-slot').forEach(el => el.classList.remove('selected'));
    document.querySelector(`[data-time="${time}"]`).classList.add('selected');
    
    showBookingForm();
}

/* BOOKING FORM */

function showBookingForm() {
    const date = new Date(selectedDate + 'T00:00:00');
    const dateDisplay = date.toLocaleDateString('en-US', { 
        weekday: 'long', 
        month: 'long', 
        day: 'numeric',
        year: 'numeric'
    });
    const timeDisplay = timeSlots.find(t => t.value === selectedTime).label;
    
    confirmDateTime.textContent = `${dateDisplay} at ${timeDisplay}`;
    
    formDate.value = selectedDate;
    formTime.value = selectedTime;
    
    bookingFormSection.style.display = 'block';
    bookingFormSection.scrollIntoView({ 
        behavior: 'smooth', 
        block: 'start' 
    });
}

/* NAVIGATION */

function navigatePreviousMonth() {
    currentDate.setMonth(currentDate.getMonth() - 1);
    renderCalendar();
}

function navigateNextMonth() {
    currentDate.setMonth(currentDate.getMonth() + 1);
    renderCalendar();
}

/* EVENT LISTENERS */

prevMonthBtn.addEventListener('click', navigatePreviousMonth);
nextMonthBtn.addEventListener('click', navigateNextMonth);

/* INITIALIZATION */

function initializeCalendar() {
    const bookedSlots = JSON.parse(bookedSlotsData.textContent);
    dateBookings = processBookedSlots(bookedSlots);
    renderCalendar();
}

document.addEventListener('DOMContentLoaded', initializeCalendar);