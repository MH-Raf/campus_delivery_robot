import math

class PhysicsEngine:
    def __init__(self, state, obstacles):
        self.state = state
        self.obstacles = obstacles
        self.target = None

        self.avoid_mode = False
        self.avoid_direction = None   
        self.is_avoiding = False

       
        self.slowdown_radius = 50.0    
        self.stop_threshold = 5.0      
        self.min_speed = 0.2           

        self.distance_travelled = 0.0

    def set_target(self, target):
        self.target = target
        self.avoid_mode = False
        self.avoid_direction = None
        self.is_avoiding = False

    def will_collide(self, x, y):
        """
        Возвращает True если точка (x,y) окажется в зоне какого-либо препятствия (с запасом).
        """
        for ox, oy, r in self.obstacles:
            if math.hypot(x - ox, y - oy) < r + 20.0:   # запас 20
                return True
        return False

    def step(self, dt):
        """
        dt — секунды (в вашем коде вы используете dt в секундах).
        self.state.position — кортеж (x,y)
        self.state.speed — текущее значение скорости (м/с)
        """
        if not self.target:
            return

        x, y = self.state.position
        tx, ty = self.target

        
        dx_goal = tx - x
        dy_goal = ty - y
        dist_goal = math.hypot(dx_goal, dy_goal)

        
        if self.avoid_mode:
            
            move_dist = max(self.state.speed * dt, 0.01)

            nx = x
            ny = y + self.avoid_direction * move_dist


            if self.will_collide(nx, ny):
                ny = y + self.avoid_direction * (move_dist * 1.5)

            
            self.state.position = (nx, ny)
            self.distance_travelled += math.hypot(nx - x, ny - y)
            self.is_avoiding = True

           
            if dist_goal > 1e-6:
                
                gx = nx + (dx_goal / dist_goal) * (self.state.speed * dt)
                gy = ny + (dy_goal / dist_goal) * (self.state.speed * dt)
                if not self.will_collide(gx, gy):
                    
                    self.avoid_mode = False
                    self.avoid_direction = None
                    self.is_avoiding = False
            return

        
        if dist_goal <= self.stop_threshold:
            
            self.state.position = (tx, ty)
            
            self.state.speed = 0.0
            return

       
        desired_speed = self.state.speed  
        
        if dist_goal < self.slowdown_radius:
            k = dist_goal / max(self.slowdown_radius, 1e-6)  # от 0..1
            desired_speed = max(self.min_speed, self.state.speed * k)

       
        step_dist = desired_speed * dt

        
        nx = x + (dx_goal / dist_goal) * step_dist
        ny = y + (dy_goal / dist_goal) * step_dist

        
        if self.will_collide(nx, ny):
            
            up_clear = True
            down_clear = True
            
            for ox, oy, r in self.obstacles:
                if math.hypot(x - ox, (y + 80.0) - oy) < r + 20.0:
                    up_clear = False
                if math.hypot(x - ox, (y - 80.0) - oy) < r + 20.0:
                    down_clear = False

            if up_clear:
                self.avoid_direction = +1
            elif down_clear:
                self.avoid_direction = -1
            else:
                
                self.avoid_direction = +1

            self.avoid_mode = True
            self.is_avoiding = True
            return

        
        self.state.position = (nx, ny)
        self.distance_travelled += step_dist

        
        alpha = 0.6
        self.state.speed = (1 - alpha) * self.state.speed + alpha * desired_speed
        
        if self.state.speed < self.min_speed and dist_goal >= self.stop_threshold:
            self.state.speed = self.min_speed
