-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Apr 29, 2025 at 10:36 AM
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
-- Database: `fraud_detection`
--

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `full_name` varchar(255) DEFAULT NULL,
  `username` varchar(150) NOT NULL,
  `password` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id`, `full_name`, `username`, `password`) VALUES
(1, NULL, 'sdsdsddsd', '$2b$12$5T.jk2I.cN6W1rFCkO3v1OwuvUMuifk4B6jhDNhT2pAoJBgfNsJjS'),
(2, NULL, 'zzzzzx', '$2b$12$LMmnegiB64AWgumFtg3XoeDdLCYFcf5IkhoSzbpgDrb48Jn15gVy6'),
(3, NULL, 'rwerrfdf', '$2b$12$1AWe3CIH2L6Nc9MmoS3fLO/uVb/dxgk3L.seEi0YQ1ChWiTuMZ3RS'),
(4, NULL, 'alex', '$2b$12$IlGxa7oaRJxihxVmbXdsRuSMCM02YwnRgkc8qZpMvMXdjTJ4K42MW'),
(5, 'AAAAAAAAA', 'nnnnnnnnn', '$2b$12$pz2N6kDdJPvJfUWbIFHkF.c.Zjb4bNxbRCpOCYg6/inGMnPFJjUvS'),
(6, 'nnnnn', 'mmmmmm', '$2b$12$xnDJJIYwgRgNEe9cEPV4wewqu5U0wFXcM1K1LeDkbCvxOOlXkl7PG'),
(7, 'user', 'user', '234'),
(8, 'vvvv', 'v', '$2b$12$weweYPpavF/v5Jo.JI5lyO.RhHZ6RTxI1W4yAGwTSo8r169PnnvJC'),
(9, 'admin', 'admin', '$2b$12$a./Ah5e9hKsqNA1GShhBzOuPHSZPVI1arG7Y49XlTtDMW5XlrsiAC');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=10;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
