"""
Kolam generation algorithms optimized for Streamlit
"""

import numpy as np
import streamlit as st
import logging

logger = logging.getLogger(__name__)

class KolamDrawV1:
    """Algorithm 1: One stroke but not complete - Streamlit optimized"""
    
    def __init__(self, ND):
        self.ND = ND
        self.Nx = ND + 1
        self.A1 = np.ones((self.Nx, self.Nx)) * 99
        self.F1 = np.ones((self.Nx, self.Nx))
        self.Ns = (2 * (ND ** 2) + 1) * 5
        self.boundary_type = 'diamond'
        
    @st.cache_data
    def get_boundaries(_self, boundary_type):
        """Cached boundary computation"""
        boundaries = {}
        for i in range(_self.Nx):
            for j in range(_self.Nx):
                if boundary_type == 'diamond':
                    boundaries[(i,j)] = abs(i - _self.ND//2) + abs(j - _self.ND//2) <= _self.ND//2
                else:
                    boundaries[(i,j)] = True
        return boundaries
    
    def is_inside_boundary(self, i, j):
        """Check if coordinates are within boundary"""
        if self.boundary_type == 'diamond':
            return abs(i - self.ND//2) + abs(j - self.ND//2) <= self.ND//2
        return True

    def ResetGateMatrix(self):
        """Reset gate and flag matrices"""
        A = self.A1.copy()
        F = self.F1.copy()
        
        # Set boundary conditions
        for i in range(self.Nx):
            A[0, i] = A[i, 0] = A[self.Nx - 1, i] = A[i, self.Nx - 1] = 0
            F[0, i] = F[i, 0] = F[self.Nx - 1, i] = F[i, self.Nx - 1] = 0
        
        return A, F

    def toss(self, bias):
        """Generate biased random value"""
        return 1 if np.random.random() > bias else 0

    def xyng(self, isv, jsv, A, theta):
        """Calculate next position"""
        directions = [(1, 1), (1, -1), (-1, -1), (-1, 1)]
        di, dj = directions[theta % 4]
        return isv + di, jsv + dj

    def generate_path(self, sigmaref):
        """Generate kolam path - main algorithm"""
        try:
            A, F = self.ResetGateMatrix()
            path = []
            
            # Start from center
            isv, jsv = self.ND // 2, self.ND // 2
            theta = 0
            
            # Progress bar for long generations
            if self.Ns > 1000:
                progress_bar = st.progress(0)
                status_text = st.empty()
            
            for step in range(self.Ns):
                if self.Ns > 1000 and step % 100 == 0:
                    progress_bar.progress(step / self.Ns)
                    status_text.text(f'Generating path... {step}/{self.Ns}')
                
                if not self.is_inside_boundary(isv, jsv):
                    break
                    
                path.append([isv, jsv])
                
                if A[isv, jsv] > 0:
                    if self.toss(sigmaref):
                        theta = (theta + 1) % 4
                    else:
                        theta = (theta - 1) % 4
                
                isv, jsv = self.xyng(isv, jsv, A, theta)
                
                # Loop detection
                if len(path) > 10 and [isv, jsv] == path[0]:
                    break
            
            # Clear progress indicators
            if self.Ns > 1000:
                progress_bar.empty()
                status_text.empty()
            
            result = np.array(path) if path else np.array([[self.ND//2, self.ND//2]])
            logger.info(f"V1 generated {len(result)} points")
            return result
            
        except Exception as e:
            logger.error(f"V1 generation error: {e}")
            st.error(f"Algorithm V1 error: {e}")
            return np.array([[self.ND//2, self.ND//2]])

class KolamDrawV2:
    """Algorithm 2: Complete pattern - Streamlit optimized"""
    
    def __init__(self, ND):
        self.ND = ND
        self.Nx = ND + 1
        self.A1 = np.ones((self.Nx, self.Nx)) * 99
        self.F1 = np.ones((self.Nx, self.Nx))
        self.Ns = 2 * (self.ND**2 + 1) + 5

    def ResetGateMatrix(self):
        """Reset matrices with completeness constraints"""
        A = self.A1.copy()
        F = self.F1.copy()
        
        # Boundary conditions
        for i in range(self.Nx):
            A[0, i] = A[i, 0] = A[self.Nx - 1, i] = A[i, self.Nx - 1] = 0
            F[0, i] = F[i, 0] = F[self.Nx - 1, i] = F[i, self.Nx - 1] = 0
        
        # Diagonal constraints
        for i in range(1, self.Nx - 1):
            A[i, i] = A[i, self.Nx - 1 - i] = 1
            F[i, i] = F[i, self.Nx - 1 - i] = 0
        
        return A, F

    def toss(self, bias):
        """Biased random generation"""
        return 1 if np.random.randint(0, 1000) / 1000 > bias else 0

    def get_valid_moves(self, i, j, A, visited):
        """Get valid next moves"""
        moves = []
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (-1, -1), (1, -1), (-1, 1)]
        
        for di, dj in directions:
            ni, nj = i + di, j + dj
            if (0 < ni < self.Nx - 1 and 0 < nj < self.Nx - 1 and 
                not visited[ni, nj] and A[ni, nj] > 0):
                moves.append((ni, nj))
        
        return moves

    def generate_single_path(self, start_i, start_j, A, F, visited, sigmaref):
        """Generate single stroke path"""
        path = []
        isv, jsv = start_i, start_j
        
        for step in range(self.Ns // 4):
            if (isv <= 0 or isv >= self.Nx - 1 or jsv <= 0 or jsv >= self.Nx - 1 or
                visited[isv, jsv] or A[isv, jsv] == 0):
                break
                
            path.append([isv, jsv])
            
            next_moves = self.get_valid_moves(isv, jsv, A, visited)
            if not next_moves:
                break
            
            if len(next_moves) > 1 and self.toss(sigmaref):
                isv, jsv = next_moves[np.random.randint(len(next_moves))]
            else:
                isv, jsv = next_moves[0]
        
        return path

    def generate_path(self, sigmaref):
        """Generate complete kolam pattern"""
        try:
            A, F = self.ResetGateMatrix()
            all_paths = []
            visited = np.zeros((self.Nx, self.Nx))
            
            # Show progress for complex generations
            progress_container = st.container()
            with progress_container:
                if self.ND > 12:
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                
                stroke_count = 0
                max_strokes = min(10, self.ND)
                total_operations = (self.Nx - 2) * (self.Nx - 2)
                current_operation = 0
                
                for start_i in range(1, self.Nx - 1):
                    for start_j in range(1, self.Nx - 1):
                        current_operation += 1
                        
                        if self.ND > 12:
                            progress_bar.progress(current_operation / total_operations)
                            status_text.text(f'Processing stroke {stroke_count + 1}/{max_strokes}...')
                        
                        if stroke_count >= max_strokes:
                            break
                            
                        if visited[start_i, start_j] or A[start_i, start_j] == 0:
                            continue
                        
                        path = self.generate_single_path(start_i, start_j, A, F, visited, sigmaref)
                        if len(path) > 3:
                            all_paths.extend(path)
                            stroke_count += 1
                            
                            # Mark visited
                            for point in path:
                                i, j = int(point[0]), int(point[1])
                                if 0 <= i < self.Nx and 0 <= j < self.Nx:
                                    visited[i, j] = 1
                    
                    if stroke_count >= max_strokes:
                        break
                
                # Clear progress indicators
                if self.ND > 12:
                    progress_bar.empty()
                    status_text.empty()
            
            result = np.array(all_paths) if all_paths else np.array([[self.ND//2, self.ND//2]])
            logger.info(f"V2 generated {len(result)} points with {stroke_count} strokes")
            return result
            
        except Exception as e:
            logger.error(f"V2 generation error: {e}")
            st.error(f"Algorithm V2 error: {e}")
            return np.array([[self.ND//2, self.ND//2]])
