-- phpMyAdmin SQL Dump
-- version 5.2.0
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Waktu pembuatan: 30 Jan 2023 pada 17.25
-- Versi server: 10.4.24-MariaDB
-- Versi PHP: 8.1.6

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `dbcrawl`
--
CREATE DATABASE IF NOT EXISTS `dbcrawl` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE `dbcrawl`;

-- --------------------------------------------------------

--
-- Struktur dari tabel `crawling`
--

CREATE TABLE `crawling` (
  `id_crawling` int(11) NOT NULL,
  `url_awal` text NOT NULL,
  `keyword` text NOT NULL,
  `total_page` int(11) NOT NULL,
  `duration_crawl` time NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Struktur dari tabel `forms`
--

CREATE TABLE `forms` (
  `id_form` int(11) NOT NULL,
  `base_url` text NOT NULL,
  `form` text NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Struktur dari tabel `images`
--

CREATE TABLE `images` (
  `id_image` int(11) NOT NULL,
  `base_url` text NOT NULL,
  `image` text NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Struktur dari tabel `linking`
--

CREATE TABLE `linking` (
  `id_linking` int(11) NOT NULL,
  `crawl_id` int(11) NOT NULL,
  `url` text NOT NULL,
  `outgoing_link` text NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Struktur dari tabel `list`
--

CREATE TABLE `list` (
  `id_list` int(11) NOT NULL,
  `base_url` text NOT NULL,
  `list` text NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Struktur dari tabel `page_information`
--

CREATE TABLE `page_information` (
  `id_pagecontent` int(11) NOT NULL,
  `base_url` text NOT NULL,
  `html5` tinyint(1) NOT NULL,
  `title` text DEFAULT NULL,
  `description` text DEFAULT NULL,
  `keywords` text DEFAULT NULL,
  `content_text` text DEFAULT NULL,
  `hot_url` tinyint(1) NOT NULL,
  `model_crawl` text NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Struktur dari tabel `script_resource`
--

CREATE TABLE `script_resource` (
  `id_script` int(11) NOT NULL,
  `base_url` text NOT NULL,
  `script` text NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Struktur dari tabel `style_resource`
--

CREATE TABLE `style_resource` (
  `id_style` int(11) NOT NULL,
  `base_url` text NOT NULL,
  `style` text NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Struktur dari tabel `tables`
--

CREATE TABLE `tables` (
  `id_table` int(11) NOT NULL,
  `base_url` text NOT NULL,
  `tables` text NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Indexes for dumped tables
--

--
-- Indeks untuk tabel `crawling`
--
ALTER TABLE `crawling`
  ADD PRIMARY KEY (`id_crawling`);

--
-- Indeks untuk tabel `forms`
--
ALTER TABLE `forms`
  ADD PRIMARY KEY (`id_form`);

--
-- Indeks untuk tabel `images`
--
ALTER TABLE `images`
  ADD PRIMARY KEY (`id_image`);

--
-- Indeks untuk tabel `linking`
--
ALTER TABLE `linking`
  ADD PRIMARY KEY (`id_linking`);

--
-- Indeks untuk tabel `list`
--
ALTER TABLE `list`
  ADD PRIMARY KEY (`id_list`);

--
-- Indeks untuk tabel `page_information`
--
ALTER TABLE `page_information`
  ADD PRIMARY KEY (`id_pagecontent`);

--
-- Indeks untuk tabel `script_resource`
--
ALTER TABLE `script_resource`
  ADD PRIMARY KEY (`id_script`);

--
-- Indeks untuk tabel `style_resource`
--
ALTER TABLE `style_resource`
  ADD PRIMARY KEY (`id_style`);

--
-- Indeks untuk tabel `tables`
--
ALTER TABLE `tables`
  ADD PRIMARY KEY (`id_table`);

--
-- AUTO_INCREMENT untuk tabel yang dibuang
--

--
-- AUTO_INCREMENT untuk tabel `crawling`
--
ALTER TABLE `crawling`
  MODIFY `id_crawling` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT untuk tabel `forms`
--
ALTER TABLE `forms`
  MODIFY `id_form` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT untuk tabel `images`
--
ALTER TABLE `images`
  MODIFY `id_image` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT untuk tabel `linking`
--
ALTER TABLE `linking`
  MODIFY `id_linking` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT untuk tabel `list`
--
ALTER TABLE `list`
  MODIFY `id_list` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT untuk tabel `page_information`
--
ALTER TABLE `page_information`
  MODIFY `id_pagecontent` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT untuk tabel `script_resource`
--
ALTER TABLE `script_resource`
  MODIFY `id_script` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT untuk tabel `style_resource`
--
ALTER TABLE `style_resource`
  MODIFY `id_style` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT untuk tabel `tables`
--
ALTER TABLE `tables`
  MODIFY `id_table` int(11) NOT NULL AUTO_INCREMENT;
--
-- Database: `skripsi`
--
CREATE DATABASE IF NOT EXISTS `skripsi` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE `skripsi`;

-- --------------------------------------------------------

--
-- Struktur dari tabel `big_data`
--

CREATE TABLE `big_data` (
  `id` int(11) NOT NULL,
  `compiled_string` longtext NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Struktur dari tabel `dictionary`
--

CREATE TABLE `dictionary` (
  `id` int(11) NOT NULL,
  `kata` varchar(255) NOT NULL,
  `one_hot_encode` text NOT NULL,
  `vector_skip_gram` text NOT NULL,
  `vector_cbow` text NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Struktur dari tabel `text`
--

CREATE TABLE `text` (
  `id` int(255) NOT NULL,
  `sumber_url` varchar(255) NOT NULL,
  `content` longtext NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Struktur dari tabel `weight`
--

CREATE TABLE `weight` (
  `id` int(11) NOT NULL,
  `metode` longtext NOT NULL,
  `matrix_weight_input` longtext NOT NULL,
  `matrix_weight_output` longtext NOT NULL,
  `kata_unik` int(11) NOT NULL,
  `hidden_layer` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Indexes for dumped tables
--

--
-- Indeks untuk tabel `big_data`
--
ALTER TABLE `big_data`
  ADD PRIMARY KEY (`id`);

--
-- Indeks untuk tabel `dictionary`
--
ALTER TABLE `dictionary`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `kata` (`kata`);

--
-- Indeks untuk tabel `text`
--
ALTER TABLE `text`
  ADD PRIMARY KEY (`id`);

--
-- Indeks untuk tabel `weight`
--
ALTER TABLE `weight`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT untuk tabel yang dibuang
--

--
-- AUTO_INCREMENT untuk tabel `big_data`
--
ALTER TABLE `big_data`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT untuk tabel `dictionary`
--
ALTER TABLE `dictionary`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT untuk tabel `text`
--
ALTER TABLE `text`
  MODIFY `id` int(255) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT untuk tabel `weight`
--
ALTER TABLE `weight`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
