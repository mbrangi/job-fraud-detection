-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: May 22, 2025 at 07:46 AM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `fake_job_db`
--

-- --------------------------------------------------------

--
-- Table structure for table `classifications`
--

CREATE TABLE `classifications` (
  `id` int(11) NOT NULL,
  `job_ad_id` int(11) NOT NULL,
  `is_fraud` tinyint(1) DEFAULT NULL,
  `reason` text DEFAULT NULL,
  `classified_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `job_ad`
--

CREATE TABLE `job_ad` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `description` text DEFAULT NULL,
  `uploaded_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `filename` varchar(255) DEFAULT NULL,
  `result` varchar(255) DEFAULT NULL,
  `reason` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `job_ad`
--

INSERT INTO `job_ad` (`id`, `user_id`, `description`, `uploaded_at`, `filename`, `result`, `reason`) VALUES
(1, 12, 'Software Developer Needed\nCompany: TechNova Solutions Ltd.\nLocation: Nairobi, Kenya\nWe are looking for a skilled software developer to join our growing team. Responsibilities include developin\nRequirements:\n- Bachelor\'s Degree in Computer Science or related field.\n- 2+ years of experience in Python or Java.\n- Knowledge of web frameworks (Django, Flask).\n- Excellent problem-solving skills.\nContact us:\nEmail: careers@technova.co.ke\nPhone: +254 712 345 678\nApplication Deadline: June 30, 2025\n', '2025-05-08 22:40:27', 'sample_job_advertisement.pdf', 'legit', 'Passed normality checks'),
(2, 12, 'Software Developer Needed\nCompany: TechNova Solutions Ltd.\nLocation: Nairobi, Kenya\nWe are looking for a skilled software developer to join our growing team. Responsibilities include developin\nRequirements:\n- Bachelor\'s Degree in Computer Science or related field.\n- 2+ years of experience in Python or Java.\n- Knowledge of web frameworks (Django, Flask).\n- Excellent problem-solving skills.\nContact us:\nEmail: careers@technova.co.ke\nPhone: +254 712 345 678\nApplication Deadline: June 30, 2025\n', '2025-05-08 23:12:39', 'sample_job_advertisement.pdf', 'legit', 'Passed normality checks'),
(3, 12, '', '2025-05-08 23:24:07', 'kndege.png', 'fake', 'Missing contact info or unrealistic content'),
(4, 12, 'Software Developer Needed\nCompany: TechNova Solutions Ltd.\nLocation: Nairobi, Kenya\nWe are looking for a skilled software developer to join our growing team. Responsibilities include developin\nRequirements:\n- Bachelor\'s Degree in Computer Science or related field.\n- 2+ years of experience in Python or Java.\n- Knowledge of web frameworks (Django, Flask).\n- Excellent problem-solving skills.\nContact us:\nEmail: careers@technova.co.ke\nPhone: +254 712 345 678\nApplication Deadline: June 30, 2025\n', '2025-05-08 23:31:33', 'sample_job_advertisement.pdf', 'legit', 'Passed normality checks'),
(5, 12, 'Software Developer Needed\nCompany: TechNova Solutions Ltd.\nLocation: Nairobi, Kenya\nWe are looking for a skilled software developer to join our growing team. Responsibilities include developin\nRequirements:\n- Bachelor\'s Degree in Computer Science or related field.\n- 2+ years of experience in Python or Java.\n- Knowledge of web frameworks (Django, Flask).\n- Excellent problem-solving skills.\nContact us:\nEmail: careers@technova.co.ke\nPhone: +254 712 345 678\nApplication Deadline: June 30, 2025\n', '2025-05-08 23:39:42', 'sample_job_advertisement.pdf', 'legit', 'Passed normality checks'),
(6, 12, 'Each step in this pipeline is important for preparing text data for a classifier. Removing non-\nletters and lowercasing standardize the format, eliminating irrelevant characters and case \ndifferences. Tokenization lets us operate on individual words. Stopword removal and stemming \nfurther simplify the vocabulary by discarding common filler words and merging word variants. \nTogether, these transformations “clean and transform raw text data” for analysis. The cleaned \ncorpus improves the quality of the data and typically leads to better model accuracy, since the \nclassifier can focus on the most informative tokens. \n \n', '2025-05-08 23:52:27', 'Each step in this pipeline is important for preparing text data for a classifier.pdf', 'legit', 'Passed normality checks'),
(7, 13, 'We are a leading international company expanding rapidly worldwide!  \nNo experience required – training provided.  \nYou can work from anywhere, any time.  \n \nJust submit your resume and start earning big TODAY!  \nLimited slots available – ACT NOW! \n \n  Apply here: www.instant-riches-foryou.biz \n \nThis opportunity has changed thousands of lives. Don’t miss out! \n \n \n', '2025-05-09 19:47:30', 'demoAdvat.pdf', 'legit', 'Passed normality checks'),
(8, 13, 'We are a leading international company expanding rapidly worldwide!  \nNo experience required – training provided.  \nYou can work from anywhere, any time.  \n \nJust submit your resume and start earning big TODAY!  \nLimited slots available – ACT NOW! \n \n  Apply here: www.instant-riches-foryou.biz \n \nThis opportunity has changed thousands of lives. Don’t miss out! \n \n \n', '2025-05-09 19:49:32', 'demoAdvat.pdf', 'legit', 'Passed normality checks'),
(9, 13, 'Acha utani basi ? \n', '2025-05-09 19:56:26', 'Acha utani basi.pdf', 'legit', 'Passed normality checks');

-- --------------------------------------------------------

--
-- Table structure for table `job_ads`
--

CREATE TABLE `job_ads` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `description` text DEFAULT NULL,
  `uploaded_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `filename` varchar(255) DEFAULT NULL,
  `result` varchar(255) DEFAULT NULL,
  `reason` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `job_ads`
--

INSERT INTO `job_ads` (`id`, `user_id`, `description`, `uploaded_at`, `filename`, `result`, `reason`) VALUES
(1, 12, 'Software Developer Needed\nCompany: TechNova Solutions Ltd.\nLocation: Nairobi, Kenya\nWe are looking for a skilled software developer to join our growing team. Responsibilities include developin\nRequirements:\n- Bachelor\'s Degree in Computer Science or related field.\n- 2+ years of experience in Python or Java.\n- Knowledge of web frameworks (Django, Flask).\n- Excellent problem-solving skills.\nContact us:\nEmail: careers@technova.co.ke\nPhone: +254 712 345 678\nApplication Deadline: June 30, 2025\n', '2025-05-08 22:40:27', 'sample_job_advertisement.pdf', 'legit', 'Passed normality checks'),
(2, 12, 'Software Developer Needed\nCompany: TechNova Solutions Ltd.\nLocation: Nairobi, Kenya\nWe are looking for a skilled software developer to join our growing team. Responsibilities include developin\nRequirements:\n- Bachelor\'s Degree in Computer Science or related field.\n- 2+ years of experience in Python or Java.\n- Knowledge of web frameworks (Django, Flask).\n- Excellent problem-solving skills.\nContact us:\nEmail: careers@technova.co.ke\nPhone: +254 712 345 678\nApplication Deadline: June 30, 2025\n', '2025-05-08 23:12:39', 'sample_job_advertisement.pdf', 'legit', 'Passed normality checks'),
(3, 12, '', '2025-05-08 23:24:07', 'kndege.png', 'fake', 'Missing contact info or unrealistic content'),
(4, 12, 'Software Developer Needed\nCompany: TechNova Solutions Ltd.\nLocation: Nairobi, Kenya\nWe are looking for a skilled software developer to join our growing team. Responsibilities include developin\nRequirements:\n- Bachelor\'s Degree in Computer Science or related field.\n- 2+ years of experience in Python or Java.\n- Knowledge of web frameworks (Django, Flask).\n- Excellent problem-solving skills.\nContact us:\nEmail: careers@technova.co.ke\nPhone: +254 712 345 678\nApplication Deadline: June 30, 2025\n', '2025-05-08 23:31:33', 'sample_job_advertisement.pdf', 'legit', 'Passed normality checks'),
(5, 12, 'Software Developer Needed\nCompany: TechNova Solutions Ltd.\nLocation: Nairobi, Kenya\nWe are looking for a skilled software developer to join our growing team. Responsibilities include developin\nRequirements:\n- Bachelor\'s Degree in Computer Science or related field.\n- 2+ years of experience in Python or Java.\n- Knowledge of web frameworks (Django, Flask).\n- Excellent problem-solving skills.\nContact us:\nEmail: careers@technova.co.ke\nPhone: +254 712 345 678\nApplication Deadline: June 30, 2025\n', '2025-05-08 23:39:42', 'sample_job_advertisement.pdf', 'legit', 'Passed normality checks'),
(6, 12, 'Each step in this pipeline is important for preparing text data for a classifier. Removing non-\nletters and lowercasing standardize the format, eliminating irrelevant characters and case \ndifferences. Tokenization lets us operate on individual words. Stopword removal and stemming \nfurther simplify the vocabulary by discarding common filler words and merging word variants. \nTogether, these transformations “clean and transform raw text data” for analysis. The cleaned \ncorpus improves the quality of the data and typically leads to better model accuracy, since the \nclassifier can focus on the most informative tokens. \n \n', '2025-05-08 23:52:27', 'Each step in this pipeline is important for preparing text data for a classifier.pdf', 'legit', 'Passed normality checks'),
(13, 13, 'We are a leading international company expanding rapidly worldwide!  \nNo experience required – training provided.  \nYou can work from anywhere, any time.  \n \nJust submit your resume and start earning big TODAY!  \nLimited slots available – ACT NOW! \n \n  Apply here: www.instant-riches-foryou.biz \n \nThis opportunity has changed thousands of lives. Don’t miss out! \n \n \n', '2025-05-09 19:47:30', 'demoAdvat.pdf', 'legit', 'Passed normality checks'),
(14, 13, 'We are a leading international company expanding rapidly worldwide!  \nNo experience required – training provided.  \nYou can work from anywhere, any time.  \n \nJust submit your resume and start earning big TODAY!  \nLimited slots available – ACT NOW! \n \n  Apply here: www.instant-riches-foryou.biz \n \nThis opportunity has changed thousands of lives. Don’t miss out! \n \n \n', '2025-05-09 19:49:32', 'demoAdvat.pdf', 'legit', 'Passed normality checks'),
(15, 13, 'Acha utani basi ? \n', '2025-05-09 19:56:26', 'Acha utani basi.pdf', 'legit', 'Passed normality checks');

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `username` varchar(100) NOT NULL,
  `fullname` varchar(100) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `role` enum('job_seeker','employer','admin') DEFAULT 'job_seeker',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id`, `username`, `fullname`, `password_hash`, `role`, `created_at`) VALUES
(5, 'alex', 'mwakalikamo', 'scrypt:32768:8:1$tAOfUR73PRxrLrpd$b7d70b9f5ed84dcc962581ad8d1de74e4dc91cf8e576ef33bc8df6274c7b0e8dd258ddc3cf3ea73401cf5c673e390d55bdd82169f2d5b64f7407390af55cbddc', 'job_seeker', '2025-05-08 19:54:41'),
(8, 'mwakalikamo', 'Alex mwakalikamo', 'scrypt:32768:8:1$npzW1rgdGvnG2QKF$32db704551e9f65ff60e92cbbec1508eb57011d6f9af5f52661c3955ab2396e925efce6802a3ee305bc3320628bd06c65a77ff177153495213803b16b6537aa4', 'job_seeker', '2025-05-08 20:00:20'),
(9, 'alexs', 'Pascal Yusuphu', 'scrypt:32768:8:1$rTksnJJtnBwk0yV2$f2de5ba207842aba01dbef650f2e742275c42456ba7d9ca3854f8dccec42e9d4613313e0aeb3df95da3945fe74b2b9cf7358125a9ef56b91142b4ace537f0de9', 'job_seeker', '2025-05-08 20:01:33'),
(10, 'ffsfsdfsdf', 'alexs', 'scrypt:32768:8:1$FyuKCdfg3ePLcLxV$097e629dc60da84a43a598aed92c724dccf1195d25255646e285ee710b59c269eb7c08f5820604d63658a91e7e62cbbfe2f5d762a1d68c691d1e6942438a9126', 'job_seeker', '2025-05-08 20:07:16'),
(11, '', '', 'scrypt:32768:8:1$bLy180sG93hwthcW$a398734ec9195282a2c44312f47904b02db0277259624688186e5933de5fcddca463405e22a4cacbd0e599b4ca10fbf4ac918e5df9709b68449a5815f8997ccc', 'job_seeker', '2025-05-08 20:23:00'),
(12, 'amina', 'Amina Ramadhani', 'scrypt:32768:8:1$fYsycXax0ZPuvlFh$5163899265ec36b427fae39fb4816e79a30d70d7eaccf0d92a3d5b3389f844b70f71b09a726a1fd8aac9b47e0b8ff1da28dd77fa358062fa85bfa3a5d2de9213', 'job_seeker', '2025-05-08 20:26:55'),
(13, 'admin', 'Florian Alex', 'scrypt:32768:8:1$tmnC0o9yEl732jT0$a4744aff0cb7f458d661d122cc8ba4c98dc24fbbc00e8302cda656abb2dcb2ed410f1d94d5adbdd793034bee4c750e9344d54836685cbaa3b92e7f21f3b03bd2', 'job_seeker', '2025-05-09 05:47:47');

-- --------------------------------------------------------

--
-- Table structure for table `user_history`
--

CREATE TABLE `user_history` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `job_ad_id` int(11) NOT NULL,
  `classification_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `classifications`
--
ALTER TABLE `classifications`
  ADD PRIMARY KEY (`id`),
  ADD KEY `job_ad_id` (`job_ad_id`);

--
-- Indexes for table `job_ad`
--
ALTER TABLE `job_ad`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `job_ads`
--
ALTER TABLE `job_ads`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`),
  ADD UNIQUE KEY `email` (`fullname`);

--
-- Indexes for table `user_history`
--
ALTER TABLE `user_history`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `job_ad_id` (`job_ad_id`),
  ADD KEY `classification_id` (`classification_id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `classifications`
--
ALTER TABLE `classifications`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `job_ad`
--
ALTER TABLE `job_ad`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=10;

--
-- AUTO_INCREMENT for table `job_ads`
--
ALTER TABLE `job_ads`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=16;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=14;

--
-- AUTO_INCREMENT for table `user_history`
--
ALTER TABLE `user_history`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `classifications`
--
ALTER TABLE `classifications`
  ADD CONSTRAINT `classifications_ibfk_1` FOREIGN KEY (`job_ad_id`) REFERENCES `job_ads` (`id`);

--
-- Constraints for table `job_ads`
--
ALTER TABLE `job_ads`
  ADD CONSTRAINT `job_ads_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);

--
-- Constraints for table `user_history`
--
ALTER TABLE `user_history`
  ADD CONSTRAINT `user_history_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
  ADD CONSTRAINT `user_history_ibfk_2` FOREIGN KEY (`job_ad_id`) REFERENCES `job_ads` (`id`),
  ADD CONSTRAINT `user_history_ibfk_3` FOREIGN KEY (`classification_id`) REFERENCES `classifications` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
