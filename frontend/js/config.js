// Same origin when served by FastAPI at /ui; falls back to localhost if opened as a file.
const API = location.protocol.startsWith('http') ? '' : 'http://localhost:8000';
const CATS = ['electricity','water','internet','classroom','hostel','cleanliness','equipment','other'];
const PRIS = ['low','medium','high','urgent'];
const STAT = [['open','Open'],['in_progress','In progress'],['resolved','Resolved'],['closed','Closed']];
const S = {
  token: localStorage.cf_token || '',
  role: localStorage.cf_role || '',
  email: localStorage.cf_email || '',
  skip: 0, limit: 10, status: '', cache: {}
};
