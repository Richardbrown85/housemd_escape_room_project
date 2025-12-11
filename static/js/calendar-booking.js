// Calendly-Style Calendar Booking JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Get booked slots data
    const bookedSlotsData = document.getElementById('booked-slots-data');
    const bookedSlots = JSON.parse(bookedSlotsData.textContent);
    
    // Process booked slots by date
    const dateBookings = {};
    bookedSlots.forEach(slot => {
        if (!dateBookings[slot.date]) {
            dateBookings[slot.date] = [];
        }
        dateBookings[slot.date].push(slot.time);
    });
    
    // Available time slots
    const timeSlots = [
        { value: '10:00', label: '10:00 AM' },
        { value: '12:00', label: '12:00 PM' },
        { value: '14:00', label: '2:00 PM' },
        { value: '16:00', label: '4:00 PM' },
        { value: '18:00', label: '6:00 PM' },
        { value: '20:00', label: '8:00 PM' }
    ];
    
    let currentDate = new Date();
    let selectedDate = null;
    let selectedTime = null;
    
    // Initialize calendar
    renderCalendar();
    
    // Month navigation
    document.getElementById('prevMonth').addEventListener('click', () => {
        currentDate.setMonth(currentDate.getMonth() - 1);
        renderCalendar();
    });
    
    document.getElementById('nextMonth').addEventListener('click', () => {
        currentDate.setMonth(currentDate.getMonth() + 1);
        renderCalendar();
    });
    
    function renderCalendar() {
        const year = currentDate.getFullYear();
        const month = currentDate.getMonth();
        
        // Update month display
        const monthNames = ['January', 'February', 'March', 'April', 'May', 'June',
                           'July', 'August', 'September', 'October', 'November', 'December'];
        document.getElementById('currentMonth').textContent = `${monthNames[month]} ${year}`;
        
        // Get calendar info
        const firstDay = new Date(year, month, 1).getDay();
        const daysInMonth = new Date(year, month + 1, 0).getDate();
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        
        // Build calendar HTML
        let html = '';
        
        // Day headers
        ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].forEach(day => {
            html += `<div class="calendar-header">${day}</div>`;
        });
        
        // Empty cells before month starts
        for (let i = 0; i < firstDay; i++) {
            html += '<div class="calendar-day disabled"></div>';
        }
        
        // Days of month
        for (let day = 1; day <= daysInMonth; day++) {
            const dateStr = `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
            const date = new Date(year, month, day);
            
            let classes = ['calendar-day'];
            
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
            
            html += `<div class="${classes.join(' ')}" data-date="${dateStr}">${day}</div>`;
        }
        
        document.getElementById('calendarGrid').innerHTML = html;
        
        // Add click handlers to dates
        document.querySelectorAll('.calendar-day:not(.past):not(.disabled)').forEach(dayEl => {
            dayEl.addEventListener('click', function() {
                selectDate(this.dataset.date);
            });
        });
    }
    
    function selectDate(dateStr) {
        selectedDate = dateStr;
        selectedTime = null;
        
        // Update calendar display
        document.querySelectorAll('.calendar-day').forEach(el => el.classList.remove('selected'));
        document.querySelector(`[data-date="${dateStr}"]`).classList.add('selected');
        
        // Show time slots
        showTimeSlots(dateStr);
    }
    
    function showTimeSlots(dateStr) {
        const booked = dateBookings[dateStr] || [];
        const date = new Date(dateStr + 'T00:00:00');
        const dateDisplay = date.toLocaleDateString('en-US', { 
            weekday: 'long', 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric' 
        });
        
        document.getElementById('selectedDateTitle').textContent = dateDisplay;
        
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
        
        document.getElementById('timeSlotsList').innerHTML = html;
        
        // Show time slots section, hide prompt
        document.getElementById('timeSlotsSection').style.display = 'block';
        document.getElementById('selectDatePrompt').style.display = 'none';
        document.getElementById('bookingFormSection').style.display = 'none';
        
        // Add click handlers to available time slots
        document.querySelectorAll('.time-slot:not(.booked)').forEach(slotEl => {
            slotEl.addEventListener('click', function() {
                selectTime(this.dataset.time);
            });
        });
    }
    
    function selectTime(time) {
        selectedTime = time;
        
        // Update time slot display
        document.querySelectorAll('.time-slot').forEach(el => el.classList.remove('selected'));
        document.querySelector(`[data-time="${time}"]`).classList.add('selected');
        
        // Show booking form
        showBookingForm();
    }
    
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
        document.getElementById('confirmDateTime').textContent = `${dateDisplay} at ${timeDisplay}`;
        
        // Set hidden form fields
        document.getElementById('formDate').value = selectedDate;
        document.getElementById('formTime').value = selectedTime;
        
        // Show form
        document.getElementById('bookingFormSection').style.display = 'block';
        
        // Scroll to form
        document.getElementById('bookingFormSection').scrollIntoView({ 
            behavior: 'smooth', 
            block: 'start' 
        });
    }
});