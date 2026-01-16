
// Import the functions you need from the SDKs you need
import { initializeApp } from "https://www.gstatic.com/firebasejs/10.13.0/firebase-app.js";
import { getAnalytics } from "https://www.gstatic.com/firebasejs/10.13.0/firebase-analytics.js";
import { getAuth, GoogleAuthProvider, signInWithPopup } from "https://www.gstatic.com/firebasejs/10.13.0/firebase-auth.js";

// Your web app's Firebase configuration
const firebaseConfig = {
    apiKey: "AIzaSyAd_a-I9U014ArpshXVAaSDL8hRHG4a4_k",
    authDomain: "web-locker-25dfe.firebaseapp.com",
    projectId: "web-locker-25dfe",
    storageBucket: "web-locker-25dfe.firebasestorage.app",
    messagingSenderId: "923162530426",
    appId: "1:923162530426:web:02b9c18d6e83c5ecb3a1c3",
    measurementId: "G-WS87WVMNSR"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const analytics = getAnalytics(app);

const auth = getAuth(app);
const provider = new GoogleAuthProvider();

export { auth, provider, signInWithPopup };
