-- phpMyAdmin SQL Dump
-- version 4.8.3
-- https://www.phpmyadmin.net/
--
-- Host: localhost
-- Generation Time: Dec 17, 2018 at 10:17 PM
-- Server version: 8.0.12
-- PHP Version: 7.1.19

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `fingerpatch`
--

-- --------------------------------------------------------

--
-- Table structure for table `ubuntu_captures`
--

CREATE TABLE `ubuntu_captures` (
  `capture_id` int(11) NOT NULL,
  `truth_id` int(11) NOT NULL DEFAULT '-1',
  `nb_flows` int(11) NOT NULL,
  `HTTP_Seq` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `Flows` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `Payload_sent` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `Payload_received` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `matched` tinyint(1) NOT NULL DEFAULT '0'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `ubuntu_cleaned_packets`
--

CREATE TABLE `ubuntu_cleaned_packets` (
  `id` int(11) NOT NULL,
  `Package` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `Version` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `Size` int(11) NOT NULL,
  `Filename` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `Depends_Summing` int(11) NOT NULL,
  `Depends_Elements_involved` int(11) NOT NULL,
  `Depends_Childrens` varchar(9000) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `Depends_Frequency` int(11) NOT NULL,
  `Depends_Freq_in_p` float NOT NULL,
  `Recommends_Summing` int(11) NOT NULL,
  `Recommends_Elements_involved` int(11) NOT NULL,
  `Recommends_Childrens` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `Recommends_Frequency` int(11) NOT NULL,
  `Recommends_Freq_in_p` float NOT NULL,
  `Suggests_Summing` bigint(64) NOT NULL,
  `Suggests_Elements_involved` int(11) NOT NULL,
  `Suggests_Childrens` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `Suggests_Frequency` int(11) NOT NULL,
  `Suggests_Freq_in_p` float NOT NULL,
  `in` tinyint(1) NOT NULL DEFAULT '0'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=COMPACT;

-- --------------------------------------------------------

--
-- Table structure for table `ubuntu_packets`
--

CREATE TABLE `ubuntu_packets` (
  `id` int(11) NOT NULL,
  `capture_id` int(30) NOT NULL,
  `Package` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `Version` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `Architecture` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `Size` int(30) NOT NULL,
  `Installed-Size` int(30) NOT NULL,
  `Priority` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `Maintainer` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `SHA1` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `Description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `parsedFrom` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `Description-md5` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `Bugs` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `Origin` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `MD5sum` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `Depends` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `Recommends` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `Suggests` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `Homepage` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `Source` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `SHA256` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `Section` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `Supported` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `Filename` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `packageMode` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `in` tinyint(1) NOT NULL DEFAULT '0'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `ubuntu_ready`
--

CREATE TABLE `ubuntu_ready` (
  `done` tinyint(1) NOT NULL,
  `id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `ubuntu_captures`
--
ALTER TABLE `ubuntu_captures`
  ADD PRIMARY KEY (`capture_id`);

--
-- Indexes for table `ubuntu_cleaned_packets`
--
ALTER TABLE `ubuntu_cleaned_packets`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `ubuntu_packets`
--
ALTER TABLE `ubuntu_packets`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `ubuntu_ready`
--
ALTER TABLE `ubuntu_ready`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `ubuntu_captures`
--
ALTER TABLE `ubuntu_captures`
  MODIFY `capture_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `ubuntu_packets`
--
ALTER TABLE `ubuntu_packets`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `ubuntu_ready`
--
ALTER TABLE `ubuntu_ready`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
