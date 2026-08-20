import { initializeApp } from "https://www.gstatic.com/firebasejs/12.14.0/firebase-app.js";
import { getAuth, signInWithEmailAndPassword, createUserWithEmailAndPassword, signOut, onAuthStateChanged, sendPasswordResetEmail } from "https://www.gstatic.com/firebasejs/12.14.0/firebase-auth.js";

const firebaseConfig = {
  apiKey: "AIzaSyCt2l9qc0HYa3Q3LdQLilVK1w-Lb_-kfH0",
  authDomain: "fake-job-detection-343c3.firebaseapp.com",
  projectId: "fake-job-detection-343c3",
  storageBucket: "fake-job-detection-343c3.firebasestorage.app",
  messagingSenderId: "931682913528",
  appId: "1:931682913528:web:c56a1716aaed0a5ab57f0d",
  measurementId: "G-NCFZ452LWY"
};

const app = initializeApp(firebaseConfig);
const auth = getAuth(app);

export { auth, signInWithEmailAndPassword, createUserWithEmailAndPassword, signOut, onAuthStateChanged, sendPasswordResetEmail };
